import asyncio
from contextlib import asynccontextmanager
from dataclasses import replace
import json
from pathlib import Path
import sqlite3
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, patch

from app.chunking.records import stable_hash
from app.chunking.tokens import count_tokens
from app.expansion.budget import Budget, BudgetExceeded, MeteredClient
from app.expansion.chunks import fragments, table
from app.expansion.context import extend
from app.expansion.parsing import FullNormalizer
from app.ingestion.normalized_models import SourceIdentity
from app.ingestion.sphinx_reader import read_corpus, parse_diagnostics
from app.pilot.release import load_release
from app.pilot.store import Store, digest
from app.retrieval.hybrid import fuse, lexical_query
from app.expansion.evaluate import comparison
from app.expansion.scoring import score_packet
from tests.pilot_fixtures import settings, KEY, retrieval


class ChunkTests(unittest.TestCase):
    def test_incomplete_fragments_do_not_claim_complete_source_evidence(self):
        case={'id':'fixture','expected_behavior':'answer','evidence_groups':[
            {'required':True,'fact':'Complete prerequisite','target_match':'all','targets':[{}]}]}
        records={str(i):{'content':{'source':{'source_path':'page'},'source_block_ids':['b1']},
                        'fragment':{'block_id':'b1','start':i*5,'end':(i+1)*5,'rendered_length':10}} for i in range(2)}
        with patch('app.expansion.scoring.target_units',return_value={('page','b1')}):
            self.assertFalse(score_packet(case,[{'chunk_id':'0'}],{'chunks':records})['all_required_groups_covered'])
            self.assertTrue(score_packet(case,[{'chunk_id':'0'},{'chunk_id':'1'}],{'chunks':records})['all_required_groups_covered'])
    def test_long_unicode_code_keeps_all_characters_and_bounds(self):
        text=('  IMPORTANT: preserve prerequisites αβγ and code indentation\n' * 150)
        parts=list(fragments(text,'Configuration'))
        self.assertGreater(len(parts),1)
        self.assertEqual(''.join(piece for _,_,piece in parts),text)
        for start,end,piece in parts:
            self.assertEqual(piece,text[start:end]);self.assertLessEqual(count_tokens('Configuration\n\n'+piece),512)

    def test_merged_table_repeats_headers_and_spanned_values(self):
        def cell(text,rs=1,cs=1):return {'kind':'table_cell','text':'','attributes':{'rowspan':rs,'colspan':cs},
            'children':[{'kind':'paragraph','text':text}]}
        def row(*cells):return {'kind':'table_row','children':list(cells)}
        b={'children':[{'kind':'table_group','attributes':{'cols':2},'children':[
            {'kind':'table_head','children':[row(cell('Method'),cell('Condition'))]},
            {'kind':'table_body','children':[row(cell('Pickup',2),cell('Available stock')),row(cell('Matching company'))]}]}]}
        text=table(b)
        self.assertIn('Method: Pickup; Condition: Available stock',text)
        self.assertIn('Method: Pickup; Condition: Matching company',text)

    def test_full_parser_keeps_spoilers_definitions_and_graphic_references(self):
        raw=b'''Setup\n=====\n\n.. spoiler:: Conditions\n\n   Important prerequisite.\n\nTerm\n   A **definition** with details.\n\n| First line\n| Second line\n\n.. card:: More\n   :target: other\n   :large:\n   :tag: Recommended\n\n   Related workflow.\n'''
        files={'content/applications/test.rst':raw}
        with read_corpus(files,full_applications=True) as (_,trees,root,logs):
            self.assertFalse([m for m,_ in parse_diagnostics(logs) if m.severity=='error'])
            source=SourceIdentity('https://github.com/odoo/documentation.git','19.0','en','a'*40,
                                  'content/applications/test.rst','b'*64,'test')
            doc=FullNormalizer(source,'test',source_root=root).normalize(trees['content/applications/test'])
            self.assertEqual(doc.status,'ok')
            self.assertIn('Important prerequisite',doc.to_json());self.assertIn('definition_list',doc.to_json())


class RetrievalTests(unittest.IsolatedAsyncioTestCase):
    def test_natural_language_lexical_query_does_not_require_every_word(self):
        self.assertEqual(lexical_query('Invoice delivered quantity, invoice?'), 'invoice OR delivered OR quantity')

    def test_hybrid_selection_requires_both_coverage_and_no_complete_regression(self):
        def score(coverage,complete):return {'scorable':True,'evidence_group_coverage':coverage,'all_required_groups_covered':complete}
        rows=[{'scores':{'dense':score(.5,True),'hybrid':score(1,False)}}]
        self.assertEqual(comparison(rows)['selected'],'dense')
        rows[0]['scores']['hybrid']['all_required_groups_covered']=True
        self.assertEqual(comparison(rows)['selected'],'hybrid')
    def test_fusion_rewards_shared_evidence_and_is_deterministic(self):
        result=fuse([{'chunk_id':'b'},{'chunk_id':'a'}],[{'chunk_id':'c'},{'chunk_id':'a'}])
        self.assertEqual(result[0]['chunk_id'],'a')
        self.assertEqual(result[0]['selection'],{'dense':2,'lexical':2})
        self.assertEqual(len({h['chunk_id'] for h in result}),3)

    async def test_expansion_is_snapshot_scoped_and_deduplicated(self):
        result=retrieval();record=result['hits'][0]['chunk_record']
        rows=[{'to_chunk_id':str(i),'relation':'reference','chunk_record':json.dumps(record)} for i in range(6)]
        db=SimpleNamespace(fetch=AsyncMock(return_value=rows))
        @asynccontextmanager
        async def connect():yield db
        with patch('app.expansion.context.connect_database',connect):
            expanded=await extend('question',result,settings('/tmp/unused'))
        self.assertEqual(len(expanded['context_hits']),5)
        self.assertEqual(db.fetch.call_args.args[1],result['snapshot_id'])
        self.assertEqual(result['hits'][0]['rank'],1)


class BudgetTests(unittest.IsolatedAsyncioTestCase):
    async def test_missing_or_exhausted_budget_prevents_provider_call(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'budget.db'
            with self.assertRaises(BudgetExceeded):Budget(path)
            Budget.approve(path,.00000001)
            client=SimpleNamespace(embeddings=SimpleNamespace(create=AsyncMock()))
            proxy=MeteredClient(client,Budget(path),{'embedding_model':'text-embedding-3-small','embedding_per_million':.02})
            with self.assertRaises(BudgetExceeded):
                await proxy.embeddings.create(model='text-embedding-3-small',input=['many tokens '*100])
            client.embeddings.create.assert_not_awaited()

    def test_reservations_survive_restart_and_approval_never_resets(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'budget.db';Budget.approve(path,1)
            Budget(path).reserve('timeout',.8)
            with self.assertRaises(BudgetExceeded):Budget(path).reserve('next',.3)
            with self.assertRaises(FileExistsError):Budget.approve(path,10)


class ReleaseTests(unittest.TestCase):
    def test_release_switch_revokes_cookie_and_preserves_history(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg=settings(tmp);store=Store(cfg.store_path);token=store.login(KEY,cfg)
            current=store.session(token,cfg)
            store.start('request',current['id'],'operations','test','19.0')
            changed=replace(cfg,release_id='full-candidate')
            self.assertIsNone(store.session(token,changed))
            self.assertEqual(len(list(store.export())),1)
            self.assertIsNotNone(store.session(store.login(KEY,changed),changed))

    def test_additive_migration_keeps_old_sessions(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg=settings(tmp)
            with sqlite3.connect(cfg.store_path) as db:
                db.execute('CREATE TABLE sessions (id TEXT PRIMARY KEY, principal TEXT, key_hash TEXT, expires REAL)')
                db.execute('INSERT INTO sessions VALUES (?,?,?,?)',(digest('legacy'),'operations',digest(KEY),time.time()+3600))
            store=Store(cfg.store_path)
            self.assertIsNotNone(store.session('legacy',cfg))

    def test_descriptor_hash_and_indexed_state_required(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'release.json'
            r={'schema_version':'odoo-release-0.1','state':'prepared'}
            p.write_text(json.dumps({'release_id':stable_hash(r),**r}))
            with self.assertRaisesRegex(ValueError,'not been indexed'):load_release(p)
            p.write_text(json.dumps({**r,'release_id':'invented'}))
            with self.assertRaisesRegex(ValueError,'identity'):load_release(p)

    def test_preview_requires_isolated_origin_store_and_cookie(self):
        from app.pilot.settings import Settings, ROOT
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'release.json'
            body={'schema_version':'odoo-release-0.1','state':'indexed_candidate',
                'snapshot_id':'b'*64,'source':{'repository_url':'https://github.com/odoo/documentation.git',
                  'commit':'a'*40,'odoo_version':'19.0','language':'en'},'corpus_name':'odoo19-full-test',
                'retrieval_method':'dense','coverage':{'documents':944,'searchable_documents':879,
                'reference_only_documents':65,'topics':['finance','sales'],'reviewed_workflows':[]}}
            p.write_text(json.dumps({'release_id':stable_hash(body),**body}))
            env={'PILOT_RELEASE_FILE':str(p),'PILOT_ACCESS_KEYS':json.dumps({'test':KEY}),
                 'PILOT_ADMIN_KEY':'distinct-test-administrator-key-123456789'}
            with patch.dict('os.environ',env,clear=True):
                with self.assertRaisesRegex(ValueError,'preview'):Settings.from_env()
                env.update(PILOT_CANDIDATE_PREVIEW='true',PILOT_PUBLIC_ORIGIN='http://localhost:8000')
                with patch.dict('os.environ',env,clear=True):
                    with self.assertRaisesRegex(ValueError,'8010'):Settings.from_env()
                env['PILOT_PUBLIC_ORIGIN']='http://localhost:8010'
                with patch.dict('os.environ',env,clear=True):
                    cfg=Settings.from_env()
                    self.assertEqual(cfg.cookie_name,'odoo_candidate_session')
                    self.assertEqual(cfg.store_path,ROOT/'data/expansion/preview.sqlite3')
                    self.assertEqual(cfg.coverage()['documents'],944)

    def test_prepared_but_unfunded_publish_never_reaches_provider_or_database(self):
        from app.expansion.publish import publish
        with tempfile.TemporaryDirectory() as tmp, patch('app.expansion.publish.publish_candidate',new_callable=AsyncMock) as provider:
            with self.assertRaises(BudgetExceeded):asyncio.run(publish(Path(tmp),Path(tmp)/'absent-budget.db'))
            provider.assert_not_awaited()

    def test_human_approval_is_bound_to_results_and_requires_solved_workflows(self):
        from app.expansion.approve import approve
        import hashlib
        from app.pilot.settings import ROOT
        with tempfile.TemporaryDirectory() as tmp:
            directory=Path(tmp)
            body={'schema_version':'odoo-release-0.1','state':'indexed_candidate','snapshot_id':'a'*64,
                'source':{'repository_url':'https://github.com/odoo/documentation.git','commit':'b'*40,
                          'odoo_version':'19.0','language':'en'},'corpus_name':'odoo19-full-fixture',
                'retrieval_method':'dense','coverage':{'documents':944,'searchable_documents':879,
                    'reference_only_documents':65,'topics':['Sales'],'reviewed_workflows':[]}}
            release={'release_id':stable_hash(body),**body}
            (directory/'release.json').write_text(json.dumps(release))
            cases=json.loads((ROOT/'evaluation/full_development.json').read_text())['cases']
            rows=[{'case_id':c['id'],'answer':{'status':'answered'}} for c in cases]
            rows += [{'case_id':f'original-{i}','answer':{'status':'answered'}} for i in range(23)]
            report={'release_id':release['release_id'],'status':'completed_pending_human_review',
                    'cases':rows,'comparison':{'selected':'hybrid'}}
            raw=json.dumps(report).encode();(directory/'evaluation.json').write_bytes(raw)
            chosen={}
            for c in cases:
                if c.get('family'):
                    chosen.setdefault(c['family'],{'case_id':c['id'],'correct':True,'complete':True,'supported':True})
            review={'reviewer':'Fixture reviewer','evaluation_sha256':hashlib.sha256(raw).hexdigest(),
                    'parser_coverage_accepted':True,'access_checks_accepted':True,
                    'no_confidently_wrong_actions':True,'workflow_cases':chosen}
            (directory/'review.json').write_text(json.dumps(review))
            approve(directory/'release.json',directory/'evaluation.json',directory/'review.json',directory/'approved.json')
            approved=load_release(directory/'approved.json')
            self.assertEqual(approved['state'],'approved');self.assertEqual(approved['retrieval_method'],'hybrid')
            self.assertEqual(len(approved['coverage']['reviewed_workflows']),6)
            review['workflow_cases']['return_credit']['complete']=False
            (directory/'review.json').write_text(json.dumps(review))
            with self.assertRaises(ValueError):
                approve(directory/'release.json',directory/'evaluation.json',directory/'review.json',directory/'rejected.json')
            self.assertFalse((directory/'rejected.json').exists())


if __name__=='__main__':unittest.main()
