# Task Planner

A small project-management app: users, projects, tasks, sprints, an audit log and reports.
Python (FastAPI) backend, Postgres, React frontend. Everything runs with Docker Compose.

## Run it

You need Docker (Docker Desktop, or Docker Engine inside WSL2) and git.

1. Clone the project and go into its folder:

   ```
   git clone https://github.com/VasuGarg07/task-planner.git
   cd task-planner
   ```

2. Create your settings file. It holds the database password and stays on your computer
   (it is git-ignored). Copy the example and change `DB_PASSWORD` to a password of your
   own, using only letters and numbers:

   ```
   cp .env.example .env
   ```

3. Start everything:

   ```
   docker compose up --build
   ```

   Compose starts Postgres, applies the migrations, then starts the API and the web page.

4. Open http://localhost:3000 for the app, or http://localhost:8000/docs for the API docs.

The app has no login. Pick who you are from the "Acting as" menu; it is sent to the API as
the `X-User-Email` header. Create a user first (Users tab), and make one a PM, because only
a PM can create projects and sprints.

Stop it with `Ctrl+C`, then `docker compose down`. Your data is kept in a Docker volume;
`docker compose down -v` deletes it.

## Develop locally

Run only the database in Docker, and the backend and frontend on your machine.

```
docker compose up -d db
cd backend
uv sync
uv run --env-file ../.env python migrate.py
uv run --env-file ../.env uvicorn app.main:app --reload
```

In VS Code, press F5 (the "Python Debugger: FastAPI" configuration) instead of the last
command to debug the backend. In a second terminal:

```
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. The dev server forwards API calls to port 8000.

`DATABASE_URL` in `.env` uses `127.0.0.1` because the backend runs on your machine. Inside
Compose the backend uses the host name `db` instead; `docker-compose.yml` sets that.

## Tests

Tests use their own database so they never touch your data. Create it once:

```
docker compose exec db psql -U vasug -d task_planner_db -c "CREATE DATABASE task_planner_test"
```

Then, from `backend/`:

```
uv run --env-file ../.env pytest
```

The tests refuse to run unless `TEST_DATABASE_URL` ends in `_test`.

## Seed sample data

With the API running, from `backend/` (this empties the tables first, so use it only on a
development database):

```
uv run --env-file ../.env python seed_via_api.py
```

## What is inside

- `backend/app/`: the API. `routers/` handle HTTP, `repository/` holds the SQL, `models.py`
  the request and response shapes, `auth.py` the identity and role checks.
- `backend/migrations/`: numbered SQL files, applied in order by `backend/migrate.py`.
- `backend/test_api.py`: all the tests, including the concurrency ones.
- `frontend/`: the React app (Vite, TypeScript), served by nginx in Docker.
- `docker-compose.yml`: Postgres, a one-off migration job, the API and the web page.
- `JOURNAL.md`: the decisions, mistakes and lessons behind each step.

## Known limitations

- Anyone can send any `X-User-Email`; there is no real login.
- If Postgres restarts, the connection pool reconnects with a growing delay, so the API
  can answer 503 for a while before it recovers.
