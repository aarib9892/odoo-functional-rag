"""Validate explicit human review and create an approved descriptor; no activation."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from app.chunking.records import stable_hash
from app.pilot.release import load_release
from app.retrieval.cli import write_report

FAMILIES={'website_order','pos_sale_return','delivery_invoicing','partial_payment','return_credit','purchase_replenishment'}


def approve(release_file, evaluation_file, review_file, output):
    release=load_release(release_file)
    raw=evaluation_file.read_bytes();evaluation=json.loads(raw);review=json.loads(review_file.read_text())
    if evaluation['release_id']!=release['release_id'] or evaluation['status']!='completed_pending_human_review':
        raise ValueError('Evaluation must have completed for this exact candidate')
    if len(evaluation['cases']) != 83 or len({r['case_id'] for r in evaluation['cases']}) != 83:
        raise ValueError('Expected all 83 development results before release review')
    if review.get('evaluation_sha256')!=hashlib.sha256(raw).hexdigest() or not review.get('reviewer','').strip():
        raise ValueError('Named review must bind the exact evaluation bytes')
    if not all(review.get(k) is True for k in ['parser_coverage_accepted','access_checks_accepted','no_confidently_wrong_actions']):
        raise ValueError('Coverage, isolation and semantic review gates must be explicitly accepted')
    reviewed=review.get('workflow_cases',{})
    if set(reviewed)!=FAMILIES:raise ValueError('All six workflow families require a reviewed example')
    cases={r['case_id']:r for r in evaluation['cases']}
    spec=json.loads((Path(__file__).resolve().parents[3]/'evaluation/full_development.json').read_text())
    family_by_id={c['id']:c.get('family') for c in spec['cases']}
    for family,item in reviewed.items():
        case_id=item['case_id']
        if (case_id not in cases or family_by_id.get(case_id)!=family or
                cases[case_id].get('answer',{}).get('status')!='answered' or
                not all(item.get(k) is True for k in ['supported','complete','correct'])):
            raise ValueError('Each selected workflow must have a complete, supported, correct answer')
    body={k:v for k,v in release.items() if k!='release_id'}
    body.update(state='approved',retrieval_method=evaluation['comparison']['selected'],
                approval={'reviewer':review['reviewer'],'evaluation_sha256':review['evaluation_sha256'],
                          'approved_at':datetime.now(timezone.utc).isoformat()})
    body['coverage']={**body['coverage'],'reviewed_workflows':sorted(FAMILIES)}
    write_report(output,{'release_id':stable_hash(body),**body})


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['release','evaluation','review','output']:p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();approve(a.release,a.evaluation,a.review,a.output)
    print('Created reviewed descriptor. Set PILOT_RELEASE_FILE and restart to activate explicitly.')


if __name__=='__main__':main()
