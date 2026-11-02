import hashlib
from pathlib import Path

from app.database import connect_database


async def apply_migration(path: Path) -> bool:
    """Apply one SQL file; return True when its recorded checksum already matches."""
    data = path.read_bytes()
    checksum = hashlib.sha256(data).hexdigest()

    async with connect_database() as connection:
        async with connection.transaction():
            await connection.execute("SELECT pg_advisory_xact_lock(3301001)")
            await connection.execute("""
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    filename TEXT PRIMARY KEY,
                    sha256 TEXT NOT NULL,
                    applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
            """)
            previous = await connection.fetchval(
                "SELECT sha256 FROM schema_migrations WHERE filename = $1",
                path.name,
            )
            if previous is not None:
                if previous != checksum:
                    raise ValueError("An applied migration file has changed")
                return True

            await connection.execute(data.decode("utf-8"))
            await connection.execute(
                "INSERT INTO schema_migrations (filename, sha256) VALUES ($1, $2)",
                path.name,
                checksum,
            )

    return False
