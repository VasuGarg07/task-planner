from collections.abc import Iterator

import psycopg
from fastapi import Request
from psycopg.rows import TupleRow
from psycopg_pool import ConnectionPool


def get_conn(request: Request) -> Iterator[psycopg.Connection[TupleRow]]:
    pool: ConnectionPool[psycopg.Connection[TupleRow]] = request.app.state.pool
    with pool.connection() as conn:
        yield conn
