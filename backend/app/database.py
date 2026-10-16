from collections.abc import Iterator
from typing import Annotated, LiteralString

import psycopg
from fastapi import Depends, Request
from psycopg.abc import Params
from psycopg.rows import TupleRow, class_row
from psycopg_pool import ConnectionPool
from pydantic import BaseModel

Connection = psycopg.Connection[TupleRow]


def get_conn(request: Request) -> Iterator[Connection]:
    pool: ConnectionPool[Connection] = request.app.state.pool
    with pool.connection() as conn:
        yield conn


DbConn = Annotated[Connection, Depends(get_conn, scope="function")]


def find_one[T: BaseModel](
    conn: Connection, model: type[T], query: LiteralString, params: Params | None = None
) -> T | None:
    with conn.cursor(row_factory=class_row(model)) as cursor:
        return cursor.execute(query, params).fetchone()


def fetch_one[T: BaseModel](
    conn: Connection, model: type[T], query: LiteralString, params: Params | None = None
) -> T:
    row = find_one(conn, model, query, params)
    if row is None:
        raise RuntimeError("Query returned no row")
    return row


def fetch_all[T: BaseModel](
    conn: Connection, model: type[T], query: LiteralString, params: Params | None = None
) -> list[T]:
    with conn.cursor(row_factory=class_row(model)) as cursor:
        return cursor.execute(query, params).fetchall()
