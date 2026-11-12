"""Exact dense + English PostgreSQL FTS, fused without application filtering."""
import json
import re

from app.database import connect_database
from app.retrieval.dense import search_dense


def lexical_query(question):
    # Natural-language questions rarely contain every exact word used by a passage.
    # OR content terms; PostgreSQL's English dictionary removes stop words.
    words = list(dict.fromkeys(re.findall(r'\w+', question.lower())))[:100]
    return ' OR '.join(words)


def fuse(dense, lexical, limit=40):
    scores, records, reasons = {}, {}, {}
    for method, hits in (("dense", dense), ("lexical", lexical)):
        for rank, hit in enumerate(hits, 1):
            key = hit['chunk_id']
            records.setdefault(key, hit)
            scores[key] = scores.get(key, 0) + 1 / (60 + rank)
            reasons.setdefault(key, {})[method] = rank
    ordered = sorted(scores, key=lambda key: (-scores[key], key))[:limit]
    return [{**records[key], 'rank': rank, 'fusion_score': scores[key],
             'selection': reasons[key]} for rank, key in enumerate(ordered, 1)]


async def search_hybrid(vector, config, question, corpus_name, top_k=20):
    dense = await search_dense(vector, config, corpus_name, top_k)
    async with connect_database() as db:
        rows = await db.fetch("""SELECT chunk_id, retrieval_text, chunk_record,
            ts_rank_cd(to_tsvector('english', retrieval_text), websearch_to_tsquery('english', $2)) AS lexical_score
            FROM index_chunks WHERE snapshot_id=$1
            AND to_tsvector('english', retrieval_text) @@ websearch_to_tsquery('english', $2)
            ORDER BY lexical_score DESC, chunk_id LIMIT $3""", dense['snapshot_id'], lexical_query(question), top_k)
    lexical = [{**dict(r), 'chunk_record': json.loads(r['chunk_record'])} for r in rows]
    return {**dense, 'schema_version': 'hybrid-rrf-0.1', 'retrieval_method': 'hybrid',
            'dense_hits': dense['hits'], 'lexical_hits': lexical,
            'hits': fuse(dense['hits'], lexical)}
