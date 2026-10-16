import os
import random
from datetime import date, timedelta

import httpx

from app.settings import get_db_conn

BASE_URL = os.environ.get("API_URL", "http://127.0.0.1:8000")

USERS = [
    ("priya.nair", "priya.nair@zenlayer.dev", "PM"),
    ("daniel.osei", "daniel.osei@zenlayer.dev", "DEV"),
    ("sara.holm", "sara.holm@zenlayer.dev", "QA"),
    ("fatima.al-sayed", "fatima.alsayed@zenlayer.dev", "BA"),
    ("ines.fischer", "ines.fischer@zenlayer.dev", "DEV-OPS"),
]

PROJECTS = [
    (
        "Customer Portal Redesign",
        "Overhaul of the self-service customer portal, moving from legacy jQuery views to a component-based frontend.",
        2,
        15,
        "IN PROGRESS",
    ),
    (
        "Payment Gateway Migration",
        "Migrate checkout and subscription billing onto the new PCI-compliant gateway with retry and webhook handling.",
        4,
        20,
        "DISCOVERY",
    ),
]

PROJECT_TRANSITIONS_PATH = {
    "NOT STARTED": [],
    "DISCOVERY": ["DISCOVERY"],
    "IN PROGRESS": ["DISCOVERY", "IN PROGRESS"],
    "COMPLETED": ["DISCOVERY", "IN PROGRESS", "COMPLETED"],
}

TASK_POOL = [
    (
        "Fix login redirect loop on Safari",
        "Users on Safari get stuck bouncing between /login and /dashboard after SSO callback.",
    ),
    (
        "Add pagination to task list endpoint",
        "GET /tasks currently returns all rows unbounded; add limit/offset with sane defaults.",
    ),
    (
        "Write unit tests for sprint capacity service",
        "Cover edge cases where story points exceed max_capacity and where sprint has zero tasks.",
    ),
    (
        "Investigate slow query on projects dashboard",
        "Dashboard load time spikes above 2s when a project has 500+ tasks.",
    ),
    (
        "Add webhook retry logic for failed payment events",
        "Currently a single failed delivery is dropped silently; add exponential backoff.",
    ),
    (
        "Design empty-state UI for analytics dashboard",
        "No mockup yet for when a team has no data in the selected date range.",
    ),
    (
        "Migrate legacy billing table to new schema",
        "Old billing_records table lacks foreign keys and has duplicate rows to dedupe.",
    ),
    (
        "Set up staging environment for payment gateway",
        "Needed before QA can run end-to-end checkout tests against sandbox credentials.",
    ),
    (
        "Fix flaky end-to-end test for checkout flow",
        "Test fails intermittently on CI, passes locally; suspect race condition in test setup.",
    ),
    (
        "Add rate limiting to public API endpoints",
        "Currently no throttling, exposing the service to abuse from unauthenticated clients.",
    ),
    (
        "Refactor auth middleware to support API keys",
        "Product wants third-party integrations to authenticate via API key, not just session cookies.",
    ),
    (
        "Update push notification templates for iOS 18",
        "New OS version changed how rich notification payloads render.",
    ),
    (
        "Write runbook for on-call rotation",
        "No documented steps for common incidents like DB connection pool exhaustion.",
    ),
    (
        "Add index on tasks.sprint_id",
        "Sprint capacity queries are doing sequential scans on the tasks table.",
    ),
    (
        "Build CSV export for support ticket volume",
        "Support lead wants a weekly export they can open in Excel.",
    ),
    (
        "Patch XSS vulnerability in comment rendering",
        "User-submitted comment text is rendered without sanitization on the task detail page.",
    ),
    (
        "Add dark mode support to customer portal",
        "Design team delivered dark mode mockups for the account settings pages.",
    ),
    (
        "Reduce cold start time for notification worker",
        "Worker takes 8s to become ready after deploy, causing dropped jobs during rollout.",
    ),
    (
        "Write integration tests for webhook signature verification",
        "No test coverage for rejecting payloads with invalid signatures.",
    ),
    (
        "Clean up unused feature flags from last quarter",
        "Several flags are fully rolled out but still gating code paths, adding complexity.",
    ),
    (
        "Add retry queue for failed email sends",
        "Transactional emails silently fail when the provider returns a 5xx.",
    ),
    (
        "Improve error messages on signup form validation",
        'Users report confusion over generic "invalid input" messages.',
    ),
    (
        "Set up centralized logging for payment service",
        "Currently logs only go to stdout, making incident debugging painful.",
    ),
    (
        "Add database backup verification job",
        "Backups run nightly but nobody verifies they can actually be restored.",
    ),
    (
        "Optimize image upload pipeline for profile photos",
        "Large uploads are not resized server-side, bloating storage costs.",
    ),
    (
        "Draft API documentation for external partners",
        "Partner integrations team has been asking for OpenAPI spec for two sprints.",
    ),
    (
        "Add feature flag for new checkout UI rollout",
        "Need gradual rollout capability before full launch to all users.",
    ),
    (
        "Fix timezone bug in sprint burndown calculation",
        "Dates are compared without normalizing timezone, causing off-by-one errors.",
    ),
    (
        "Harden input validation on task creation endpoint",
        "Missing validation allows empty task names and negative story points.",
    ),
    (
        "Spike: evaluate message queue options for notifications",
        "Compare RabbitMQ vs SQS for the new notification worker architecture.",
    ),
    (
        "Add CI pipeline caching for faster builds",
        "Build times increased significantly after adding new test suites, slowing down PR feedback loops.",
    ),
    (
        "Fix duplicate charge bug in subscription renewal",
        "Some customers are billed twice when a subscription renews on a failed card retry.",
    ),
    (
        "Add health check endpoint for notification worker",
        "Kubernetes cannot currently tell if the worker pod is ready to receive jobs.",
    ),
    (
        "Write migration script for legacy user roles",
        "Old role names (admin, member) need mapping to the new RBAC role enum.",
    ),
    (
        "Add search functionality to task list view",
        "Users want to filter tasks by keyword without scrolling through pages.",
    ),
    (
        "Fix broken pagination links on mobile viewport",
        "Next/prev buttons overlap with content on screens under 400px wide.",
    ),
    (
        "Add Slack alert integration for failed deployments",
        "On-call currently only finds out about failed deploys by checking CI manually.",
    ),
    (
        "Optimize N+1 query on task list with assignee join",
        "Task list endpoint issues one query per task to fetch assignee details.",
    ),
    (
        "Add soft delete support for projects",
        "Deleting a project currently cascades and permanently removes all tasks and sprints.",
    ),
    (
        "Write load test for checkout endpoint",
        "Need to validate the payment gateway migration can handle peak Black Friday traffic.",
    ),
]

TASK_STATUS_WEIGHTS = [
    ("OPEN", []),
    ("IN PROGRESS", ["IN PROGRESS"]),
    ("DONE", ["IN PROGRESS", "DONE"]),
    ("ON HOLD", ["ON HOLD"]),
    ("VOID", ["VOID"]),
]
TASK_STATUS_PROBABILITY = [0.25, 0.2, 0.3, 0.15, 0.1]

STORY_POINTS = [1, 2, 3, 5, 8]


def request(
    method: str, path: str, email: str, payload: dict[str, object]
) -> int | None:
    response = httpx.request(
        method, f"{BASE_URL}{path}", headers={"X-User-Email": email}, json=payload
    )
    if response.status_code >= 400:
        print(
            f"  ! {method} {path} failed ({response.status_code}): {response.text.strip()}"
        )
        return None
    return int(response.json()["id"])


def require(created_id: int | None) -> int:
    if created_id is None:
        raise SystemExit("Seeding stopped: a required request failed")
    return created_id


def reset_database() -> None:
    with get_db_conn() as conn:
        conn.execute(
            "TRUNCATE TABLE logs, tasks, sprints, projects, users RESTART IDENTITY CASCADE"
        )
    print("Database truncated.")


def seed_users() -> dict[str, int]:
    print("Creating users...")
    email_to_id: dict[str, int] = {}
    for username, email, role in USERS:
        body: dict[str, object] = {"username": username, "email": email, "role": role}
        user_id = request("POST", "/users", email, body)
        if user_id is not None:
            email_to_id[email] = user_id
    print(f"  {len(email_to_id)} users created.")
    return email_to_id


def seed_projects_and_sprints(pm_email: str) -> list[tuple[int, int, list[int]]]:
    print("Creating projects and sprints...")
    plans: list[tuple[int, int, list[int]]] = []
    today = date.today()

    for name, description, sprint_count, task_count, target_status in PROJECTS:
        project_body: dict[str, object] = {"name": name, "description": description}
        project_id = require(request("POST", "/projects", pm_email, project_body))

        for step_status in PROJECT_TRANSITIONS_PATH[target_status]:
            status_body: dict[str, object] = {"status": step_status}
            request("PATCH", f"/projects/{project_id}/status", pm_email, status_body)

        sprint_ids: list[int] = []
        for n in range(1, sprint_count + 1):
            offset_weeks = sprint_count - n + 1
            start = today - timedelta(weeks=2 * offset_weeks)
            end = start + timedelta(days=13)
            sprint_body: dict[str, object] = {
                "project_id": project_id,
                "name": f"Sprint {n}",
                "start_date": start.isoformat(),
                "end_date": end.isoformat(),
                "max_capacity": 20 + n * 5,
            }
            sprint_id = require(request("POST", "/sprints", pm_email, sprint_body))
            sprint_ids.append(sprint_id)

            if end < today:
                for sprint_status in ["ACTIVE", "COMPLETED"]:
                    body: dict[str, object] = {"status": sprint_status}
                    request("PATCH", f"/sprints/{sprint_id}/status", pm_email, body)
            elif start <= today <= end:
                body = {"status": "ACTIVE"}
                request("PATCH", f"/sprints/{sprint_id}/status", pm_email, body)

        plans.append((project_id, task_count, sprint_ids))

    sprint_total = sum(len(sprint_ids) for _, _, sprint_ids in plans)
    print(f"  {len(plans)} projects, {sprint_total} sprints created.")
    return plans


def seed_tasks(
    plans: list[tuple[int, int, list[int]]],
    email_to_id: dict[str, int],
    pm_email: str,
) -> None:
    print("Creating tasks...")
    emails = [email for _, email, _ in USERS]
    total_created = 0

    for project_id, task_count, sprint_ids in plans:
        for title, description in random.sample(TASK_POOL, task_count):
            reporter_email = random.choice(emails)
            task_body: dict[str, object] = {
                "project_id": project_id,
                "name": title,
                "description": description,
                "assignee_id": email_to_id[random.choice(emails)],
            }
            task_id = request("POST", "/tasks", reporter_email, task_body)
            if task_id is None:
                continue
            total_created += 1

            if random.random() < 0.2:
                assign_body: dict[str, object] = {
                    "assignee_id": email_to_id[random.choice(emails)]
                }
                request(
                    "PATCH", f"/tasks/{task_id}/assign", reporter_email, assign_body
                )

            points_body: dict[str, object] = {
                "story_points": random.choice(STORY_POINTS)
            }
            request(
                "PATCH", f"/tasks/{task_id}/story-points", reporter_email, points_body
            )

            if sprint_ids and random.random() < 0.7:
                add_body: dict[str, object] = {"task_id": task_id}
                sprint_id = random.choice(sprint_ids)
                request("PATCH", f"/sprints/{sprint_id}/add-task", pm_email, add_body)

            _, path = random.choices(
                TASK_STATUS_WEIGHTS, weights=TASK_STATUS_PROBABILITY
            )[0]
            for step_status in path:
                status_body: dict[str, object] = {"status": step_status}
                request(
                    "PATCH", f"/tasks/{task_id}/status", reporter_email, status_body
                )

    print(f"  {total_created} tasks created.")


def main() -> None:
    reset_database()
    email_to_id = seed_users()
    pm_email = USERS[0][1]
    plans = seed_projects_and_sprints(pm_email)
    seed_tasks(plans, email_to_id, pm_email)
    print("Done.")


if __name__ == "__main__":
    main()
