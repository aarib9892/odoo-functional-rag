CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE index_snapshots (
    snapshot_id TEXT PRIMARY KEY,
    chunk_snapshot_id TEXT NOT NULL,
    embedding_snapshot_id TEXT NOT NULL,
    embedding_config_id TEXT NOT NULL,
    embedding_config JSONB NOT NULL CHECK (
        jsonb_typeof(embedding_config) = 'object'
        AND embedding_config @> '{"dimensions": 1536}'::jsonb
    ),
    expected_chunks INTEGER NOT NULL CHECK (expected_chunks > 0),
    metadata JSONB NOT NULL CHECK (jsonb_typeof(metadata) = 'object'),
    published BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    published_at TIMESTAMPTZ,
    UNIQUE (snapshot_id, embedding_config_id),
    UNIQUE (snapshot_id, published),
    CHECK (published = (published_at IS NOT NULL))
);

CREATE TABLE embeddings (
    cache_key TEXT PRIMARY KEY,
    embedding_config_id TEXT NOT NULL,
    text_sha256 TEXT NOT NULL,
    embedding VECTOR(1536) NOT NULL CHECK (vector_norm(embedding) > 0),
    UNIQUE (cache_key, embedding_config_id, text_sha256)
);

CREATE TABLE index_chunks (
    snapshot_id TEXT NOT NULL,
    chunk_id TEXT NOT NULL,
    embedding_record_id TEXT NOT NULL,
    embedding_config_id TEXT NOT NULL,
    cache_key TEXT NOT NULL,
    text_sha256 TEXT NOT NULL,
    retrieval_text TEXT NOT NULL CHECK (length(btrim(retrieval_text)) > 0),
    chunk_record JSONB NOT NULL CHECK (jsonb_typeof(chunk_record) = 'object'),
    PRIMARY KEY (snapshot_id, chunk_id),
    UNIQUE (snapshot_id, embedding_record_id),
    FOREIGN KEY (snapshot_id, embedding_config_id)
        REFERENCES index_snapshots (snapshot_id, embedding_config_id),
    FOREIGN KEY (cache_key, embedding_config_id, text_sha256)
        REFERENCES embeddings (cache_key, embedding_config_id, text_sha256),
    CHECK (text_sha256 = encode(sha256(convert_to(retrieval_text, 'UTF8')), 'hex')),
    CHECK ((chunk_record ->> 'chunk_id') IS NOT DISTINCT FROM chunk_id),
    CHECK ((chunk_record #>> '{content,retrieval_text}') IS NOT DISTINCT FROM retrieval_text)
);

CREATE TABLE active_indexes (
    corpus_name TEXT PRIMARY KEY CHECK (length(btrim(corpus_name)) > 0),
    snapshot_id TEXT NOT NULL,
    published BOOLEAN NOT NULL DEFAULT TRUE CHECK (published),
    FOREIGN KEY (snapshot_id, published)
        REFERENCES index_snapshots (snapshot_id, published)
);