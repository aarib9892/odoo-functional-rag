"""Prepare immutable full-app snapshots, links and cost estimate without API/DB calls."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path

from app.chunking.eligibility import assess_chunk, ELIGIBILITY_VERSION
from app.chunking.records import stable_hash
from app.chunking.snapshot import fingerprint
from app.chunking.tokens import count_tokens
from app.embeddings.cache import EmbeddingCache
from app.embeddings.config import EmbeddingConfig, embedding_cache_key
from app.embeddings.inputs import load_embedding_inputs
from app.expansion.chunks import CONFIG, chunks
from app.ingestion.normalize_corpus import write_snapshot
from app.ingestion.repository import get_clean_commit
from app.retrieval.cli import write_report
from app.pilot.settings import ROOT


def walk(items):
    for item in items:
        yield item
        yield from walk(item.get('items', item.get('children', [])))


def links(documents, records, decisions):
    eligible = {r['chunk_id'] for r, d in zip(records, decisions) if d['eligible_for_retrieval']}
    by_path, by_block = defaultdict(list), defaultdict(list)
    for r in records:
        if r['chunk_id'] not in eligible: continue
        c = r['content']; path = c['source']['source_path']
        by_path[path].append(r)
        for block in c['source_block_ids']: by_block[path, block].append(r['chunk_id'])
    edges = set(); unresolved = []
    for path, page in by_path.items():
        for first, second in zip(page, page[1:]):
            for a, b in ((first, second), (second, first)):
                edges.add((a['chunk_id'], b['chunk_id'], 'neighbor'))
    for path, doc in documents.items():
        for root in walk(doc['items']):
            if 'block_id' not in root: continue
            owners = by_block.get((path, root['block_id']), [])
            if not owners: continue
            for child in walk([root]):
                for inline in walk(child.get('inlines', [])):
                    a = inline.get('attributes', {})
                    if inline.get('kind') != 'reference': continue
                    target = a.get('destination_path')
                    if a.get('resolution') != 'resolved' or target not in documents:
                        unresolved.append({'from': path, 'target': a.get('target'), 'resolution': a.get('resolution')})
                        continue
                    candidates = by_path.get(target, [])
                    anchor = a.get('destination_anchor')
                    if anchor:
                        sections = {s['section_id'] for s in walk(documents[target]['items'])
                                    if anchor in s.get('anchors', [])}
                        candidates = [r for r in candidates if r['content']['section_id'] in sections]
                    if candidates:
                        for owner in owners:
                            dest = candidates[0]['chunk_id']
                            if owner != dest: edges.add((owner, dest, 'reference'))
                    else:
                        unresolved.append({'from': path, 'target': target, 'resolution': 'no_searchable_target'})
    return sorted(edges), unresolved


def prepare(directory, pricing, cache_path):
    audit = json.loads((directory/'audit/audit.json').read_text())
    manifest = json.loads((directory/'manifest.json').read_text())
    if audit['inventory_fingerprint'] != manifest['inventory_fingerprint'] or audit['status'] != 'audited':
        raise ValueError('Audit does not match manifest')
    if len(audit['pages']) != 944 or len({p['source_path'] for p in audit['pages']}) != 944:
        raise ValueError('Expected all 944 pages')
    errors = [d for d in audit['parser_diagnostics'] if d['severity'] == 'error']
    if errors or any(p['status'] != 'ok' for p in audit['pages']):
        raise ValueError('Corpus has unreviewed parser/content failures; inspect audit.json')
    if get_clean_commit(ROOT/'sources/odoo-documentation') != audit['source']['commit']:
        raise ValueError('Source changed since audit')
    docs = {}; records = []; decisions = []; pages = []; failures = []
    for row in audit['pages']:
        path = row['source_path']
        doc = json.loads((directory/'audit/documents'/(path[:-4]+'.json')).read_text())
        if doc['source']['sha256'] != next(r['sha256'] for r in manifest['inventory']['files'] if r['source_path']==path):
            raise ValueError('Audited source identity mismatch')
        docs[path] = doc
        try:
            page_records = chunks(doc)
            page_decisions = [assess_chunk(r, doc) for r in page_records]
            records.extend(page_records); decisions.extend(page_decisions)
            pages.append({'source_path': path, 'application': row['application'],
                          'classification': 'searchable' if any(d['eligible_for_retrieval'] for d in page_decisions) else 'reference_only',
                          'chunks': len(page_records), 'images': sum(b.get('kind')=='image' for b in walk(doc['items']))})
        except Exception as error:
            failures.append({'source_path': path, 'error': str(error)})
    write_report(directory/'chunk-audit.json', {'pages': pages, 'failures': failures})
    if failures: raise ValueError(f'{len(failures)} chunking failures; inspect chunk-audit.json')
    summary = {'schema_version':'m22-0.2','normalizer_version':'full-app-structures-0.2',
               'source':audit['source'],'inventory_fingerprint':audit['inventory_fingerprint'], 'normalized_documents':len(docs)}
    payload = {'documents/'+p[:-4]+'.json': (json.dumps(d,sort_keys=True,ensure_ascii=False)+'\n').encode() for p,d in docs.items()}
    payload['summary.json']=(json.dumps(summary,sort_keys=True)+'\n').encode()
    normalized, _ = write_snapshot(directory/'normalized', payload)
    chunk_summary = {**summary,'schema_version':'m31-chunk-snapshot-0.2','normalized_snapshot_id':normalized.name,
        'chunk_records':len(records),'chunking_config_id':stable_hash(CONFIG),'chunking_config':CONFIG,
        'largest_chunk_tokens':max(r['token_count'] for r in records),'retrieval_eligibility':'classified',
        'eligibility_version':ELIGIBILITY_VERSION,'eligible_chunk_records':sum(d['eligible_for_retrieval'] for d in decisions),
        'metadata_only_chunk_records':sum(not d['eligible_for_retrieval'] for d in decisions)}
    def jsonl(items): return ''.join(json.dumps(r,sort_keys=True,ensure_ascii=False)+'\n' for r in items).encode()
    chunk_path, _ = write_snapshot(directory/'chunks', {'chunks.jsonl':jsonl(records),'eligibility.jsonl':jsonl(decisions),
        'summary.json':(json.dumps(chunk_summary,sort_keys=True)+'\n').encode()})
    edges, unresolved = links(docs, records, decisions)
    write_report(directory/'links.json', {'chunk_snapshot_id':chunk_path.name, 'edges':edges,'unresolved':unresolved})
    config = EmbeddingConfig(); cache = EmbeddingCache(cache_path); unique = {}
    for item in load_embedding_inputs(chunk_path): unique.setdefault(embedding_cache_key(item,config), item)
    missing = [item for item in unique.values() if cache.load(item, config) is None]
    tokens = sum(count_tokens(item.text) for item in missing)
    rates = json.loads(pricing.read_text())
    if rates['embedding_model'] != config.model: raise ValueError('Pricing model mismatch')
    estimate = {'schema_version':'expansion-cost-0.1','state':'awaiting_budget_selection','provider_calls_made':0,
        'normalized_snapshot':str(normalized),'chunk_snapshot':str(chunk_path),'source':audit['source'],
        'pages':len(pages),'page_classes':dict(Counter(p['classification'] for p in pages)),
        'applications':dict(Counter(p['application'] for p in pages)), 'chunks':len(records),
        'unique_embedding_inputs':len(unique),'cache_hits':len(unique)-len(missing),'new_embeddings':len(missing),
        'uncached_embedding_tokens':tokens,'embedding_estimate_usd':round(tokens*rates['embedding_per_million']/1e6,6),
        'reference_edges':sum(e[2]=='reference' for e in edges),'neighbor_edges':sum(e[2]=='neighbor' for e in edges),
        'image_references':sum(p['images'] for p in pages),'pricing':rates,
        'evaluation':{'development_cases':83,'generation_calls_max':166,
            'assumed_input_tokens_per_call':10000,'max_output_tokens_per_call':2400,
            'generation_estimate_usd':round(166*(10000*rates['input_per_million']+2400*rates['output_per_million'])/1e6,6),
            'query_embedding_upper_tokens':83*8192,
            'query_embedding_upper_usd':round(83*8192*rates['embedding_per_million']/1e6,6),
            'note':'Planning estimate, not a quote or hard bound on billed generation input. No caching discount assumed; includes reasoning in output allowance.'}}
    write_report(directory/'estimate.json',estimate)
    print(json.dumps({k:v for k,v in estimate.items() if k not in {'source','pricing','applications'}},indent=2))
    return estimate


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--directory',type=Path,default=ROOT/'data/expansion')
    p.add_argument('--pricing',type=Path,default=ROOT/'config/expansion.pricing.json')
    p.add_argument('--cache',type=Path,default=ROOT/'data/embeddings/cache')
    a=p.parse_args();prepare(a.directory.resolve(),a.pricing,a.cache)


if __name__=='__main__':main()
