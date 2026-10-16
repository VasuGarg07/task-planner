import os

import psycopg
from psycopg.rows import TupleRow


def get_database_url() -> str:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError(
            "DATABASE_URL is not set. Define it in .env, see .env.example"
        )
    return database_url


def get_db_conn() -> psycopg.Connection[TupleRow]:
    return psycopg.connect(get_database_url())
