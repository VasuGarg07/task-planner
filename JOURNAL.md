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
