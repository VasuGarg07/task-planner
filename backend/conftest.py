import os
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

import migrate
from app.main import app
from app.settings import get_db_conn


@pytest.fixture(scope="session", autouse=True)
def test_database() -> Iterator[None]:
    test_url = os.environ["TEST_DATABASE_URL"]
    assert test_url.endswith("_test")
    with pytest.MonkeyPatch.context() as patch:
        patch.setenv("DATABASE_URL", test_url)
        migrate.main()
        yield


@pytest.fixture(autouse=True)
def clean_tables() -> None:
    with get_db_conn() as conn:
        conn.execute(
            "TRUNCATE users, projects, tasks, sprints, logs RESTART IDENTITY CASCADE"
        )


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client
