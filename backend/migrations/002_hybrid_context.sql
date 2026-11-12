CREATE INDEX IF NOT EXISTS index_chunks_english_fts
    ON index_chunks USING GIN (to_tsvector('english', retrieval_text));

CREATE TABLE IF NOT EXISTS chunk_links (
    snapshot_id TEXT NOT NULL,
    from_chunk_id TEXT NOT NULL,
    to_chunk_id TEXT NOT NULL,
    relation TEXT NOT NULL CHECK (relation IN ('reference', 'neighbor')),
    PRIMARY KEY (snapshot_id, from_chunk_id, to_chunk_id, relation),
    FOREIGN KEY (snapshot_id, from_chunk_id) REFERENCES index_chunks(snapshot_id, chunk_id),
    FOREIGN KEY (snapshot_id, to_chunk_id) REFERENCES index_chunks(snapshot_id, chunk_id),
    CHECK (from_chunk_id <> to_chunk_id)
);
