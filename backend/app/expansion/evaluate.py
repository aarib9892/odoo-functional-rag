"""Metered candidate comparison and answer diagnostics; no automatic activation."""
import argparse
import asyncio
from dataclasses import replace
import hashlib
import json
from pathlib import Path
from statistics import fmean
from time import perf_counter
from uuid import uuid4

from dotenv import load_dotenv
from openai import AsyncOpenAI
from app.embeddings.cache import EmbeddingCache
from app.evaluation.evidence import build_evidence_index, score_case
from app.expansion.budget import Budget, BudgetExceeded, MeteredClient
from app.expansion.context import extend
from app.expansion.scoring import score_packet
from app.pilot.evidence import build_evidence
from app.pilot.generation import Generator
from app.pilot.release import load_release
from app.pilot.service import AnswerService
from app.pilot.settings import ROOT, Settings
from app.retrieval.cli import write_report
from app.retrieval.query import retrieve_question


def comparison(rows):
    eligible=[r for r in rows if r.get('scores',{}).get('dense',{}).get('scorable')]
    if not eligible: return {'selected':'dense','reason':'No reviewed evidence cases scored'}
    scores={method:{'mean_group_coverage':fmean(r['scores'][method]['evidence_group_coverage'] for r in eligible),
                    'complete_evidence_rate':fmean(r['scores'][method]['all_required_groups_covered'] for r in eligible)}
            for method in ('dense','hybrid')}
    better=(scores['hybrid']['mean_group_coverage']>scores['dense']['mean_group_coverage'] and
            scores['hybrid']['complete_evidence_rate']>=scores['dense']['complete_evidence_rate'])
    return {'selected':'hybrid' if better else 'dense','reviewed_cases':len(eligible),'scores':scores,
            'reason':'Coverage improvement without complete-evidence regression' if better else 'Retain dense control'}


async def evaluate(directory, budget_file):
    budget=Budget(budget_file)
    release=load_release(directory/'candidate-release.json')
    estimate=json.loads((directory/'estimate.json').read_text())
    specification=(ROOT/'evaluation/benchmark.json').read_bytes()
    if hashlib.sha256(specification).hexdigest()!='e1d893f01c13c23f1f3014f65d5045ff1c4015534b9b57edb76226b290fd8425':
        raise ValueError('Frozen benchmark changed')
    original=[{**c,'origin':'original'} for c in json.loads(specification)['cases'] if c['split']=='development']
    added=[{**c,'origin':'expanded'} for c in json.loads((ROOT/'evaluation/full_development.json').read_text())['cases']]
    cases=original+added
    index=build_evidence_index(Path(estimate['normalized_snapshot']),Path(estimate['chunk_snapshot']),ROOT/'sources/odoo-documentation')
    cfg=replace(Settings.from_env(),snapshot_id=release['snapshot_id'],source_commit=release['source']['commit'],
        corpus_name=release['corpus_name'],release_id=release['release_id'],full_applications=True,
        document_count=944,topics=tuple(release['coverage']['topics']))
    output=directory/'evaluations'/(str(uuid4())+'.json')
    report={'schema_version':'full-evaluation-0.1','release_id':release['release_id'],
            'status':'running','cases':[],'activation_allowed':False}
    results={}
    async with AsyncOpenAI(timeout=45,max_retries=0) as base:
        client=MeteredClient(base,budget,json.loads((ROOT/'config/expansion.pricing.json').read_text()))
        try:
            for case in cases:
                started=perf_counter()
                found=await retrieve_question(case['question'],EmbeddingCache(cfg.query_cache),cfg.corpus_name,20,
                    client=client,method='hybrid',expected_snapshot_id=cfg.snapshot_id)
                dense={**found,'hits':found['dense_hits']}
                results[case['id']]={'dense':dense,'hybrid':found}
                row={'case_id':case['id'],'question':case['question'],'origin':case['origin'],
                     'retrieval_ms':round((perf_counter()-started)*1000),'scores':{},'evidence':{}}
                for method, result in results[case['id']].items():
                    context=await extend(case['question'],result,cfg)
                    evidence=build_evidence(context,cfg,budget=6000)
                    row['evidence'][method]=evidence
                    if case['origin']=='original':
                        row['scores'][method]=score_packet(case,evidence,index)
                    else: row['scores'][method]={'scorable':False,'reason':'pending_human_review'}
                report['cases'].append(row);write_report(output,report)
            report['comparison']=comparison(report['cases'])
            method=report['comparison']['selected']
            for row,case in zip(report['cases'],cases):
                async def cached(*args, _result=results[case['id']][method], **kwargs): return _result
                service=AnswerService(replace(cfg,retrieval_method=method),
                    Generator(cfg.model,client,cfg.reasoning_effort,full_applications=True),retriever=cached)
                telemetry={}
                async with asyncio.timeout(cfg.request_timeout):
                    row['answer']=await service.answer(case['question'],'19.0',[],str(uuid4()),client,telemetry)
                row['audit']=telemetry.get('_audit');row['human_verdict']='pending'
                write_report(output,report)
            report['status']='completed_pending_human_review'
        except Exception as error:
            report['status']='budget_exhausted' if isinstance(error,BudgetExceeded) else 'failed'
            report['error']={'type':type(error).__name__}
    write_report(output,report);print('Saved:',output)
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--directory',type=Path,default=ROOT/'data/expansion')
    p.add_argument('--budget',type=Path,required=True);a=p.parse_args()
    load_dotenv(ROOT/'backend/.env');load_dotenv(ROOT/'backend/.env.pilot')
    asyncio.run(evaluate(a.directory,a.budget))


if __name__=='__main__':main()
