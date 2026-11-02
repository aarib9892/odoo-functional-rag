from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
import os

import asyncpg


@asynccontextmanager
async def connect_database() -> AsyncIterator[asyncpg.Connection]:
    password = os.environ.get("ODOO_RAG_DB_PASSWORD")
    if not password:
        raise ValueError("ODOO_RAG_DB_PASSWORD must be set")

    port = int(os.environ.get("ODOO_RAG_DB_PORT", "55433"))
    if not 1 <= port <= 65535:
        raise ValueError("ODOO_RAG_DB_PORT must be between 1 and 65535")

    connection = await asyncpg.connect(
        host=os.environ.get("ODOO_RAG_DB_HOST") or "127.0.0.1",
        port=port,
        user=os.environ.get("ODOO_RAG_DB_USER") or "odoo_rag",
        database=os.environ.get("ODOO_RAG_DB_NAME") or "odoo_rag",
        password=password,
        timeout=10.0,
        command_timeout=30.0,
        server_settings={"application_name": "odoo-functional-rag"},
    )
    try:
        yield connection
    finally:
        await connection.close(timeout=5.0)
