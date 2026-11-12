"""Conservative evidence coverage: a fragment never credits an entire source block."""
from collections import defaultdict
from app.evaluation.evidence import target_units


def score_packet(case, evidence, index):
    if case['expected_behavior']!='answer':
        return {'scorable':False,'reason':'requires_behavior_evaluation'}
    units=set();partial=defaultdict(list)
    for passage in evidence:
        record=index['chunks'][passage['chunk_id']]
        content=record['content'];path=content['source']['source_path']
        if 'fragment' not in record:
            units.update((path,b) for b in content['source_block_ids'])
        else:
            f=record['fragment'];partial[path,f['block_id']].append((f['start'],f['end'],f['rendered_length']))
    for unit,ranges in partial.items():
        covered=0;lengths={r[2] for r in ranges}
        if len(lengths)!=1: raise ValueError('Conflicting fragment lengths')
        for start,end,length in sorted(ranges):
            if not 0<=start<end<=length: raise ValueError('Invalid fragment range')
            if start>covered:break
            covered=max(covered,end)
        if covered==next(iter(lengths)):units.add(unit)
    groups=[]
    for group in case['evidence_groups']:
        if not group['required']:continue
        matches=[target_units(t,index)<=units for t in group['targets']]
        if group['target_match'] not in {'all','any'} or not matches:raise ValueError('Invalid evidence group')
        covered=all(matches) if group['target_match']=='all' else any(matches)
        groups.append({'fact':group['fact'],'covered':covered})
    if not groups:raise ValueError('Reviewed answerable case needs evidence groups')
    return {'scorable':True,'case_id':case['id'],
        'alignment_version':index.get('alignment_version','')+'+whole-fragment-blocks-0.1',
        'evidence_group_coverage':sum(g['covered'] for g in groups)/len(groups),
        'all_required_groups_covered':all(g['covered'] for g in groups),'groups':groups}
