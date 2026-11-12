"""One-hop verified reference/neighbor expansion in the same immutable snapshot."""
import json
from app.database import connect_database


async def extend(question, result, settings):
    if result['snapshot_id'] != settings.snapshot_id:
        raise ValueError('Context snapshot differs from release')
    seeds = result['hits'][:8]
    ids = [h['chunk_id'] for h in seeds]
    async with connect_database() as db:
        rows = await db.fetch("""SELECT l.to_chunk_id, l.relation, c.chunk_record
            FROM chunk_links l JOIN index_chunks c
            ON c.snapshot_id=l.snapshot_id AND c.chunk_id=l.to_chunk_id
            WHERE l.snapshot_id=$1 AND l.from_chunk_id=ANY($2::text[])
            AND NOT (l.to_chunk_id=ANY($2::text[]))
            ORDER BY CASE l.relation WHEN 'reference' THEN 0 ELSE 1 END,
                array_position($2::text[], l.from_chunk_id), l.to_chunk_id LIMIT 40""", settings.snapshot_id, ids)
    seen = set(ids)
    extras = []
    for row in rows:
        if row['to_chunk_id'] in seen:
            continue
        seen.add(row['to_chunk_id'])
        extras.append({'chunk_id': row['to_chunk_id'], 'chunk_record': json.loads(row['chunk_record']),
                       'selection': {'expansion': row['relation']}})
        if len(extras) == 4:
            break
    return {**result, 'context_hits': [*seeds, *extras], 'context_policy': 'full-app-links-0.1',
            'support_chunk_ids': [h['chunk_id'] for h in extras]}
