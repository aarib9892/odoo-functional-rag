"""Budget-gated import into a candidate namespace. Never activates the pilot alias."""
import argparse
import asyncio
import json
from pathlib import Path

from dotenv import load_dotenv
from openai import AsyncOpenAI
from app.chunking.records import stable_hash
from app.chunking.snapshot import read_files, fingerprint
from app.database import connect_database
from app.embeddings.cache import EmbeddingCache
from app.embeddings.config import EmbeddingConfig
from app.indexing.publish import publish_candidate
from app.migrate import apply_migration
from app.expansion.budget import Budget, MeteredClient
from app.pilot.settings import ROOT
from app.retrieval.cli import write_report


async def publish(directory, budget_path):
    budget=Budget(budget_path)  # Refuse before any database/provider operation if not approved.
    estimate=json.loads((directory/'estimate.json').read_text())
    chunk_path=Path(estimate['chunk_snapshot']); files=read_files(chunk_path)
    if fingerprint(files)!=chunk_path.name: raise ValueError('Candidate snapshot was changed')
    summary=json.loads(files['summary.json'])
    if summary['normalized_documents']!=944 or summary['source']!=estimate['source']:
        raise ValueError('Publication must use the audited full-application corpus')
    graph=json.loads((directory/'links.json').read_text())
    if graph['chunk_snapshot_id']!=chunk_path.name: raise ValueError('Graph belongs to another snapshot')
    prices=json.loads((ROOT/'config/expansion.pricing.json').read_text())
    corpus='odoo19-full-'+chunk_path.name[:16]
    async with AsyncOpenAI(timeout=45,max_retries=0) as client:
        result=await publish_candidate(chunk_path,directory/'embeddings',EmbeddingConfig(),
            EmbeddingCache(ROOT/'data/embeddings/cache'),corpus_name=corpus,
            client=MeteredClient(client,budget,prices))
    await apply_migration(ROOT/'backend/migrations/002_hybrid_context.sql')
    async with connect_database() as db:
        async with db.transaction():
            await db.executemany('INSERT INTO chunk_links VALUES ($1,$2,$3,$4) ON CONFLICT DO NOTHING',
                [(result['database_snapshot_id'],*edge) for edge in graph['edges']])
    body={'schema_version':'odoo-release-0.1','state':'indexed_candidate','corpus_name':corpus,
          'snapshot_id':result['database_snapshot_id'],'source':estimate['source'], 'retrieval_method':'dense',
          'coverage':{'documents':944,'topics':[{'hr':'Human Resources','general':'General settings',
                      'inventory_and_mrp':'Inventory & Manufacturing'}.get(a,a.replace('_',' ').title())
                      for a in sorted(estimate['applications'])], 'reviewed_workflows':[],
                      'searchable_documents':estimate['page_classes']['searchable'],
                      'reference_only_documents':estimate['page_classes']['reference_only']}}
    release={'release_id':stable_hash(body),**body}
    write_report(directory/'candidate-release.json',release)
    write_report(directory/'publication.json',result)
    print('Indexed isolated candidate:',directory/'candidate-release.json')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--directory',type=Path,default=ROOT/'data/expansion')
    p.add_argument('--budget',type=Path,required=True);a=p.parse_args()
    load_dotenv(ROOT/'backend/.env');asyncio.run(publish(a.directory.resolve(),a.budget))


if __name__=='__main__':main()
