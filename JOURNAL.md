# Task Planner: Journal

A project-management API (users, projects, tasks, sprints, audit log) being rewritten from
Flask to FastAPI, then given a React frontend, Docker, and CI. Stack: Python, FastAPI,
Postgres (Docker), pytest.

This is a dev diary, newest entries at the bottom. One or two paragraphs each. Entries
that record a choice start with "Decision:" and name the option I rejected.

## 2026-10-16: Kickoff
Decision: rewrite from scratch instead of porting the Flask code line by line. Rejected a
port: it would carry over Flask-shaped habits (blueprints, decorators for auth and logging,
`config.json` with a password, one pool in `db.py`) that FastAPI handles differently
(routers, dependencies, models, `.env`). A rewrite forces me to understand each piece.
Cost: slower, and the old code must stay as a behavior reference until parity (it is
deleted in the last step). I chose FastAPI because short-links already taught me the stack,
and it gives typed request models and automatic `/docs` for free.

Set up the repo like short-links: one git repo, backend in `backend/` (uv), `.vscode`
for debugging. F5 now starts uvicorn with `cwd` set to `backend/`; my first attempt failed
with "Could not import module main" because VS Code ran from the repo root.

## 2026-10-16: Step 1 layout
Decision: a package (`backend/app/`) instead of a flat `main.py` like short-links.
Rejected flat: with 24 endpoints, four resources, auth and an audit log it would get
crowded, and the old project already split `routes/` and `repository/`. Cost: the launch
target becomes `app.main:app`, and imports are slightly longer.

## 2026-10-16: Steps 2 and 3, settings and Postgres
Decision: plain `os.environ` in one module (`app/settings.py`) instead of a settings library
like pydantic-settings. Rejected the library: it is a new dependency that hides what is
happening, and I could not yet explain what it does. Cost: I write the "missing variable"
error myself. The database URL is `postgresql://user:password@127.0.0.1:5432/task_planner_db`.
It uses `127.0.0.1` because Postgres runs in Docker inside WSL2 and the port is published to
my machine; `db` (the Compose service name) only works for another container, which will
matter in Step 17. Learned that `.env` is loaded only by VS Code's `envFile` when I press F5,
so a plain terminal does not see it. Running a script there gave a bare `KeyError`.

Compose runs only Postgres 18 (pinned), bound to `127.0.0.1`, with a named volume at
`/var/lib/postgresql` and a `pg_isready` healthcheck. Same shape as short-links, new database
name `task_planner_db`. The `POSTGRES_*` variables only apply when the volume is empty, so
changing the password later needs the volume deleted.

## 2026-10-16: Step 4, migrations
Decision: a small runner (`backend/migrate.py`) that records applied files in a
`schema_migrations` table, instead of mounting the folder into `docker-entrypoint-initdb.d`
like short-links. Rejected the init folder: it only runs on an empty volume, so every new
migration would mean deleting my data. Cost: about 25 lines to write and understand. Each file
and its `schema_migrations` row run in one transaction, so a failing file leaves nothing behind.

Decision: improved the old schema while splitting it into three files (basic tables, sprints,
logs). Identity columns instead of `SERIAL`, `TIMESTAMPTZ` with a default for `created_at`,
`sprints.project_id NOT NULL`, and a foreign key from `logs.actor_id` to `users` with
`ON DELETE SET NULL` so the log survives a deleted user. Renamed `logs.timestamp` to
`created_at`. Rejected keeping the old schema as-is: it had a `DATE` with no default and a log
column that could point at a user that never existed.

## 2026-10-16: Step 5, connection pool
Decision: a connection pool (`psycopg_pool`, sync `ConnectionPool`) created once in the app
lifespan and borrowed per request through a dependency, instead of one connection per request
like short-links. Rejected per-request connections: opening a Postgres connection is
expensive, and Postgres caps total connections (100 by default), so it does not survive load.
It was a mistake to skip the pool in short-links. Pool settings: sizes 1 and 10, `timeout=3` so
a dead database fails fast, `check_connection` so dead sockets are replaced, `open=False`
because the implicit `open=True` default is going to change. A global handler turns
`OperationalError` and `PoolTimeout` into a 503. A try/except inside `/health` would not work,
because the borrow happens in the dependency before the endpoint body runs.

Checked current docs and forum advice: lifespan plus a sync pool for plain `def` endpoints is
still the standard. Considered a module-level pool (shorter) and lifespan state with
`request.state`. Kept `app.state`: a module-level pool reads the URL at import time, which
would make the test database easy to bypass. In production the real work is the arithmetic:
workers x `max_size` x instances must stay under Postgres's connection limit, usually with
PgBouncer in front.

Tested by stopping and starting the database container while the server ran: `/health` gave
200, then 503 after exactly 3 seconds (the pool `timeout`) with the server still up, then
200 again after the container came back. Recovery was not instant: it was still 503 about
two and a half minutes after the restart, even though a direct connection worked. The pool
retries with exponential backoff (1s, 2s, 4s and so on), so after a long outage the next
attempt can be minutes away. Fine for local work, but something to tune before relying on it.

## 2026-10-16: Step 6, test setup
Decision: a separate database `task_planner_test` in the same container, instead of a test
schema inside the dev database or a throwaway container per run. Rejected the schema: a wrong
setting could wipe real dev data. Rejected a container per run: slow, and I do not need that
isolation yet. `conftest.py` asserts the test URL ends with `_test`, runs the migrations on
it, then truncates all tables before every test. `TestClient` must be used with `with`, or the
lifespan never runs and there is no pool.

The first test run caught a real bug: `003_logs.sql` had `INTEGER` split across two lines.
The runner applied `001` and `002` and rolled `003` back, so the transaction design worked.
Tests run with `uv run --env-file ../.env pytest` from `backend/`. Proved the guard: I
inserted a sentinel user into the dev database, pointed `TEST_DATABASE_URL` at the dev database
on purpose, and pytest stopped on the assertion before touching anything. The sentinel row was
still there afterwards, and I deleted it.

## 2026-10-16: Steps 7 to 12, all resources
Built users, auth, projects, tasks, sprints, the audit log and the reports in one pass, with
38 tests (success, 404, validation error, forbidden role, state conflicts, logs, reports).
`mypy --strict` and ruff are clean; I ran them with `uvx`, so they are not project
dependencies yet. Layout: `app/models.py` (Pydantic models), `app/repository/` (raw SQL, one
file per resource), `app/routers/` (HTTP only), plus `database.py`, `auth.py`, `errors.py` and
`pagination.py`. Each resource got its own repository functions and router, same shape every
time, so the later ones were mostly copying a pattern I already understood.

Decision: repository functions return Pydantic models through psycopg's `class_row`, instead
of tuples plus `dict(zip(columns, row))` like the Flask code. Rejected tuples: `row[8]` is
unreadable, and it hid a real bug in the old sprint capacity check: it read `sprint_id`
(index 8) where it meant `story_points` (index 9). Cost: one small model per shape.

Decision: `Depends(get_conn, scope="function")`. Per the `Depends` docs, a `yield` dependency by default
runs its exit code after the response is sent, and my pool commits on exit, so a client could get
201 before the commit and never learn that the commit failed. Function scope commits first,
and an `HTTPException` raised mid-request rolls everything back.

Decision: the audit log is an explicit `add_log(...)` call inside each endpoint, in the same
transaction as the change, instead of the old `@log_action` decorator. Rejected the decorator:
it wrote the log in a separate connection after the work, parsed the response body to find
the ids, and a failed request could leave a change without its log. Now a rejected request
writes no log (there is a test for it). Project deletes are not logged because
`logs.project_id` cascades and the rows would vanish with the project.

Decision: identity is still the `X-User-Email` header (401 without it, 403 for an unknown
email). Only the PM role is enforced (create or delete project, project status, create sprint,
add task to sprint, sprint status). I now require identity on every endpoint except `/users`
and `/health`; the old list endpoints for projects and tasks were open by accident. `/users`
stays open because the first user has to be created somehow. Known limitation: anyone can
send any email.

Behavior changes from the Flask version, on purpose: creates return the created object with
201, deletes return 204, and "valid request in the wrong state" is 409 (illegal status
transition, sprint over capacity, duplicate name or email) instead of 400. A reference to a
row that does not exist (bad `project_id` or `assignee_id`) is 400 through a foreign-key
handler. `GET /users?email=` returns a list instead of a single user or 404. List endpoints
now order by id, because `LIMIT`/`OFFSET` without `ORDER BY` can repeat or skip rows. The
workload report returns an empty report for a project with no assigned tasks, where the old
code answered 404, and the project logs answer 404 only for an unknown project.

## 2026-10-16: Flask code removed
Deleted `app.py`, `routes/`, `repository/`, `middlewares/`, `db.py`, `schema.sql` and
`requirements.txt` in one commit. The new app covers all 24 endpoints from the inventory, and
the old behavior is recorded above, so the reference code was no longer needed.
