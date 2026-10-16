import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import psycopg
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from psycopg.rows import TupleRow
from psycopg_pool import ConnectionPool, PoolTimeout

from app.database import DbConn
from app.routers import projects, sprints, tasks, users
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
app.include_router(users.router)
app.include_router(projects.router)
app.include_router(tasks.router)
app.include_router(sprints.router)


@app.exception_handler(psycopg.OperationalError)
@app.exception_handler(PoolTimeout)
def database_unavailable(request: Request, error: Exception) -> JSONResponse:
    logger.error("Database unavailable: %s", error)
    return JSONResponse(status_code=503, content={"detail": "Database unavailable"})


@app.exception_handler(psycopg.errors.UniqueViolation)
def already_exists(request: Request, error: Exception) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": "Already exists"})


@app.exception_handler(psycopg.errors.ForeignKeyViolation)
def reference_missing(request: Request, error: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=400, content={"detail": "Referenced record does not exist"}
    )


@app.get("/health")
def health(conn: DbConn) -> dict[str, str]:
    conn.execute("SELECT 1")
    return {"status": "ok", "database": "up"}
