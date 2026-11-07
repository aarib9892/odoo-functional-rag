"""Initialize/verify this project's DB from saved vectors; no provider calls.

Refuse to replace a different active index. Never delete or reset any database.
"""
import asyncio
from dotenv import load_dotenv

from app.database import connect_database
from app.indexing.importer import import_index
from app.migrate import apply_migration
from app.pilot.settings import ACCEPTED_INDEX, ROOT


async def bootstrap():
    async with connect_database() as db:
        exists = await db.fetchval("SELECT to_regclass('public.active_indexes') IS NOT NULL")
        if exists:
            current = await db.fetchval("SELECT snapshot_id FROM active_indexes WHERE corpus_name='odoo19'")
            if current is not None and current != ACCEPTED_INDEX:
                raise ValueError("A different index is active; review it before changing the pilot corpus")
    await apply_migration(ROOT / "backend/migrations/001_dense_index.sql")
    snapshot, reused = await import_index(
        ROOT / "data/chunks/corpus/2648e24f59b6233ba8417f79a9607a663c714aef00057193767e4383c6b85dce",
        ROOT / "data/embeddings/corpus/6e2c657ee8cd109c40c928024916ba5f0803bbee65e6a0abadfdf47dddb4343c")
    if snapshot != ACCEPTED_INDEX:
        raise ValueError("Unexpected imported snapshot")
    print("Verified existing index:" if reused else "Imported saved index:", snapshot)


def main():
    load_dotenv(ROOT / "backend/.env")
    asyncio.run(bootstrap())


if __name__ == "__main__":
    main()
