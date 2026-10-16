import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated

import psycopg
from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from psycopg.rows import TupleRow
from psycopg_pool import ConnectionPool, PoolTimeout

from app.database import get_conn
from app.settings import get_database_url

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    with ConnectionPool[psycopg.Connection[TupleRow]](
        get_database_url(),
        min_size=1,
        max_size=10,
        timeout=3,
        open=False,
        check=ConnectionPool.check_connection,
    ) as pool:
        app.state.pool = pool
        yield


app = FastAPI(lifespan=lifespan)


@app.exception_handler(psycopg.OperationalError)
@app.exception_handler(PoolTimeout)
def database_unavailable(request: Request, error: Exception) -> JSONResponse:
    logger.error("Database unavailable: %s", error)
    return JSONResponse(status_code=503, content={"detail": "Database unavailable"})


@app.get("/health")
def health(
    conn: Annotated[psycopg.Connection[TupleRow], Depends(get_conn)],
) -> dict[str, str]:
    conn.execute("SELECT 1")
    return {"status": "ok", "database": "up"}
