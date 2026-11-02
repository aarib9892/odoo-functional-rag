import asyncio
import hashlib
import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
from unittest.mock import patch
from uuid import uuid4

from app.database import connect_database
from app.embeddings.cache import EmbeddingCache
from app.embeddings.config import EmbeddingConfig
from app.embeddings.inputs import load_embedding_inputs
from app.indexing.candidate import prepare_candidate
from app.indexing.rebuild import rebuild_corpus
from app.retrieval.dense import search_dense


def git(repository, *arguments):
    return subprocess.run(
        ["git", "-C", str(repository), *arguments],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def manifest_for(repository, url):
    records = []
    for path in sorted(repository.glob("content/**/*.rst")):
        data = path.read_bytes()
        records.append(
            {
                "source_path": path.relative_to(repository).as_posix(),
                "application": "sales",
                "size_bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            }
        )

    inventory = {
        "source": {
            "repository_url": url,
            "odoo_version": "19.0",
            "language": "en",
            "commit": git(repository, "rev-parse", "HEAD"),
        },
        "files": records,
    }
    encoded = json.dumps(inventory, sort_keys=True, separators=(",", ":")).encode()

    return {
        "inventory": inventory,
        "inventory_fingerprint": hashlib.sha256(encoded).hexdigest(),
    }


async def database_state(corpus="odoo19"):
    async with connect_database() as connection:
        active = await connection.fetchval(
            "SELECT snapshot_id FROM active_indexes WHERE corpus_name = $1",
            corpus,
        )
        counts = dict(await connection.fetchrow("""
            SELECT (SELECT count(*) FROM index_snapshots) AS snapshots,
                   (SELECT count(*) FROM index_chunks) AS chunks,
                   (SELECT count(*) FROM embeddings) AS embeddings,
                   (SELECT count(*) FROM active_indexes) AS active
        """))
    return active, counts


async def source_paths(snapshot):
    async with connect_database() as connection:
        rows = await connection.fetch(
            """
            SELECT DISTINCT
                   chunk_record #>> '{content,source,source_path}' AS path
            FROM index_chunks WHERE snapshot_id = $1
        """,
            snapshot,
        )
    return {row["path"] for row in rows}


async def cleanup(corpus, url):
    async with connect_database() as connection:
        async with connection.transaction():
            rows = await connection.fetch(
                """
                SELECT snapshot_id FROM index_snapshots
                WHERE metadata #>> '{chunk_summary,source,repository_url}' = $1
            """,
                url,
            )
            snapshots = [row["snapshot_id"] for row in rows]

            rows = await connection.fetch(
                """
                SELECT DISTINCT cache_key FROM index_chunks
                WHERE snapshot_id = ANY($1::text[])
            """,
                snapshots,
            )
            keys = [row["cache_key"] for row in rows]

            await connection.execute(
                "DELETE FROM active_indexes WHERE corpus_name = $1",
                corpus,
            )
            await connection.execute(
                "DELETE FROM index_chunks WHERE snapshot_id = ANY($1::text[])",
                snapshots,
            )
            await connection.execute(
                "DELETE FROM index_snapshots WHERE snapshot_id = ANY($1::text[])",
                snapshots,
            )
            await connection.execute(
                """
                DELETE FROM embeddings e
                WHERE e.cache_key = ANY($1::text[])
                AND NOT EXISTS (
                    SELECT 1 FROM index_chunks c
                    WHERE c.cache_key = e.cache_key
                )
            """,
                keys,
            )


async def main():
    tag = uuid4().hex
    corpus = "m3-lifecycle-" + tag
    url = "https://fixture.invalid/" + tag + ".git"
    before = await database_state()

    with TemporaryDirectory(prefix="m3-lifecycle-") as directory:
        root = Path(directory)
        repository = root / "source"
        repository.mkdir()

        git(repository, "init", "-q")
        git(repository, "config", "user.name", "Lifecycle Fixture")
        git(repository, "config", "user.email", "fixture@example.invalid")

        pages = repository / "content/applications/sales/sales"
        pages.mkdir(parents=True)
        cache = EmbeddingCache(root / "cache")
        config = EmbeddingConfig()

        def write_page(name, body):
            title = name + " " + tag
            (pages / (name + ".rst")).write_text(
                title + "\n" + "=" * len(title) + "\n\n" + body + "\n",
                encoding="utf-8",
            )

        def commit(message):
            git(repository, "add", "-A")
            git(repository, "commit", "-qm", message)

        async def build(previous):
            manifest = manifest_for(repository, url)
            _, chunks = prepare_candidate(
                repository,
                manifest,
                root / "data/normalized/corpus",
                root / "data/chunks/corpus",
            )

            inputs = load_embedding_inputs(chunks)
            missing = [item for item in inputs if cache.load(item, config) is None]

            for item in missing:
                vector = [0.0] * 1536
                vector[0] = 1.0
                vector[1] = int(item.text_sha256[:8], 16) / 0xFFFFFFFF
                cache.store(item, config, vector)

            result = await rebuild_corpus(
                repository,
                manifest,
                previous,
                root / "data",
                config,
                cache,
                corpus_name=corpus,
            )
            assert result["generation"]["api_requests"] == 0

            return manifest, result, len(inputs) - len(missing), len(missing)

        try:
            with patch(
                "app.embeddings.job.AsyncOpenAI",
                side_effect=AssertionError(
                    "Real API clients are forbidden in this probe"
                ),
            ):
                for name in ("edited", "kept", "removed"):
                    write_page(name, "Version one of " + name + " " + tag)

                commit("initial fixture")
                old, first, reused, seeded = await build(None)

                assert len(first["source_changes"]["added"]) == 3
                assert (reused, seeded) == (0, 3), (reused, seeded)

                write_page("edited", "Version two of edited " + tag)
                write_page("added", "Newly added page " + tag)
                (pages / "removed.rst").unlink()
                commit("add edit remove fixture")

                current, second, reused, seeded = await build(old)

                assert (reused, seeded) == (1, 2), (reused, seeded)
                assert {
                    name: len(paths) for name, paths in second["source_changes"].items()
                } == {
                    "added": 1,
                    "changed": 1,
                    "unchanged": 1,
                    "removed": 1,
                }

                active = second["database_snapshot_id"]
                assert active != first["database_snapshot_id"]
                assert (await database_state(corpus))[0] == active

                expected = {
                    record["source_path"] for record in current["inventory"]["files"]
                }
                assert await source_paths(active) == expected

                removed = (pages / "removed.rst").relative_to(repository).as_posix()

                assert removed in await source_paths(first["database_snapshot_id"])
                assert removed not in await source_paths(active)

                retrieved = await search_dense(
                    [1.0] + [0.0] * 1535,
                    config,
                    corpus_name=corpus,
                    top_k=3,
                )
                contents = [hit["chunk_record"]["content"] for hit in retrieved["hits"]]

                assert {
                    content["source"]["source_path"] for content in contents
                } == expected
                assert all(
                    content["source"]["commit"]
                    == current["inventory"]["source"]["commit"]
                    for content in contents
                )

                edited = next(
                    content
                    for content in contents
                    if content["source"]["source_path"].endswith("/edited.rst")
                )
                assert "Version two of edited" in edited["retrieval_text"]
                assert "Version one of edited" not in edited["retrieval_text"]

                repeated = await rebuild_corpus(
                    repository,
                    current,
                    current,
                    root / "data",
                    config,
                    cache,
                    corpus_name=corpus,
                )
                assert (
                    repeated["database_snapshot_id"] == active
                ), "Unchanged rebuild changed the snapshot ID"
                assert repeated["generation"]["cache_hits"] == 3
                assert len(repeated["source_changes"]["unchanged"]) == 3

                write_page(
                    "edited",
                    "Broken page\n\n.. unknown_fixture_directive::",
                )
                commit("broken parser fixture")
                failed = manifest_for(repository, url)
                state = await database_state(corpus)

                try:
                    await rebuild_corpus(
                        repository,
                        failed,
                        current,
                        root / "data",
                        config,
                        cache,
                        corpus_name=corpus,
                    )
                except ValueError:
                    pass
                else:
                    raise AssertionError("Invalid RST was published")

                assert await database_state(corpus) == state
                assert await source_paths(active) == expected

                print(
                    "Real source changes: " "1 added, 1 changed, 1 unchanged, 1 removed"
                )
                print("Unchanged text reused: 1; " "new fixture vectors seeded: 2")
                print(
                    "Removed page absent from active index; "
                    "retained in history: passed"
                )
                print(
                    "Dense retrieval contains updated text "
                    "and only the new commit: passed"
                )
                print(
                    "Unchanged rebuild and real " "parser-failure preservation: passed"
                )
        finally:
            await cleanup(corpus, url)
            assert await database_state() == before

    print("Fixture database records cleaned; production pointer/counts unchanged")
    print("Real API requests: 0; fixture vectors only")


if __name__ == "__main__":
    asyncio.run(main())
