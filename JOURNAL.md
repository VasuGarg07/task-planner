# Task Planner: Journal

A project-management API (users, projects, tasks, sprints, audit log) rewritten from Flask to
FastAPI, then given a React frontend and Docker Compose. Newest entries at the bottom. A line
that starts with "Decision:" names the option I rejected.

## 2026-10-16: Setup (steps 0 to 3)
- Decision: rewrite from scratch, not a line-by-line port. A port would keep Flask habits
  (blueprints, decorators, `config.json`). Cost: slower, and the old code stayed as a reference.
- Decision: a package (`backend/app/`), not one `main.py`. 24 endpoints would crowd a flat file.
- Decision: settings from plain `os.environ`, not a settings library. No new dependency, and I
  can explain every line.
- The database URL uses `127.0.0.1` when the backend runs on my machine and `db` inside Compose.
- Learned: VS Code needs `cwd` set to `backend/`, and only VS Code loads `.env`. A terminal needs
  `uv run --env-file`.

## 2026-10-16: Database and tests (steps 4 to 6)
- Decision: my own migration runner (`migrate.py`, one transaction per file), not Postgres's init
  folder. The init folder runs only on an empty volume.
- Schema changes while splitting `schema.sql`: identity columns, `TIMESTAMPTZ` with defaults,
  `sprints.project_id NOT NULL`, and `logs.actor_id` as a foreign key with `ON DELETE SET NULL`.
- Decision: a connection pool created in the app lifespan, not one connection per request
  (that was a mistake in short-links). Settings: 1 to 10 connections, 3 second timeout. A global
  handler turns database errors into 503.
- After a database restart the pool recovers slowly (it retries with a growing delay), so `/health`
  can stay at 503 for minutes.
- Decision: a separate `task_planner_test` database. `conftest.py` refuses to run unless the URL
  ends in `_test`; I proved it by pointing it at the dev database on purpose.
- The first test run caught a typo in a migration, and the transaction rolled it back cleanly.

## 2026-10-16: The API (steps 7 to 12)
- Structure: `models.py`, `repository/` (raw SQL), `routers/`. 38 tests; `mypy --strict` and ruff pass.
- Decision: repositories return Pydantic models (`class_row`), not tuples. Tuples hid an old bug
  where the sprint capacity check read `sprint_id` instead of `story_points`.
- Decision: `Depends(get_conn, scope="function")`, so the commit happens before the response is sent.
- Decision: the audit log is written inside the request's transaction, not by a decorator. A
  rejected request writes no log. Project deletes are not logged (the rows cascade away).
- Identity is still the `X-User-Email` header, and only PM is enforced. Every endpoint except
  `/users` and `/health` now needs it. Known limitation: anyone can send any email.
- Changes from Flask, on purpose: creates return the object (201), deletes return 204, wrong-state
  requests return 409, list endpoints order by id.

## 2026-10-16: Seed script and concurrency (steps 14 and 15)
- Seed script moved to `backend/seed_via_api.py`, rewritten with `httpx`, and it drives the real API.
- Mistake: my first seed run hit the dev database, because an old server held the port. Before
  running a truncate, check which database the server on the other end uses.
- Two races, shown by tests first: sprint capacity failed 8 of 10 runs (weight 6 or 7 against a
  limit of 5), and conflicting status changes failed 10 of 10.
- Decision: two different fixes. Capacity is a sum over many rows, so I lock the sprint row
  (`SELECT ... FOR UPDATE`). A status change touches one row, so it is compare-and-set
  (`UPDATE ... WHERE status = old`, 409 if no row). Rejected `SERIALIZABLE` with retries.

## 2026-10-16: Frontend and Docker (steps 16 and 17)
- A screen for every endpoint, using Vite, React, TypeScript and plain `fetch`. The status menus
  show every status and the API's 409 message, so the server keeps the rules.
- Decision: React Router and Lucide icons, and every API call under `/api` (Vite and nginx strip
  the prefix). Without it, a reload on `/projects/3` would be forwarded to the API.
- Styling is plain CSS: a sidebar layout, avatars, and one `data-status` attribute for every
  status color.
- Decision: Compose runs `db`, a one-off `migrate` job, `backend` (waits for `migrate`) and
  `frontend` (nginx). Rejected running migrations at backend start, where replicas would race.
- Tested the app in the browser (board, status errors, task details, sprints, reports, activity log).

## 2026-10-16: Close-out (steps 18 and 19)
- Decision: skipped CI for now. Cost: tests and linters only run when I run them.
- Removed the Flask code, `requirements.txt`, `schema.sql`, `db.py` and `config.json`.
- Process mistake: my commits carried a Claude co-author line and were made unasked, so the
  history was rewritten and the rule is saved.
