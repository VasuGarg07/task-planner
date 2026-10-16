from concurrent.futures import ThreadPoolExecutor

from fastapi.testclient import TestClient

Headers = dict[str, str]


def register(client: TestClient, role: str = "BA") -> Headers:
    email = f"{role.lower()}@example.com"
    client.post("/users", json={"username": role.lower(), "email": email, "role": role})
    return {"X-User-Email": email}


def create_project(client: TestClient, pm: Headers, name: str = "Alpha") -> int:
    response = client.post(
        "/projects", json={"name": name, "description": "About"}, headers=pm
    )
    return int(response.json()["id"])


def create_task(
    client: TestClient,
    headers: Headers,
    project_id: int,
    name: str = "Task 1",
    **extra: object,
) -> int:
    body = {"project_id": project_id, "name": name, **extra}
    response = client.post("/tasks", json=body, headers=headers)
    return int(response.json()["id"])


def create_sprint(
    client: TestClient, pm: Headers, project_id: int, max_capacity: int = 10
) -> int:
    body = {
        "project_id": project_id,
        "name": "Sprint 1",
        "start_date": "2026-01-01",
        "end_date": "2026-01-14",
        "max_capacity": max_capacity,
    }
    response = client.post("/sprints", json=body, headers=pm)
    return int(response.json()["id"])


def test_health_reports_database_up(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "up"}


def test_create_user_returns_user(client: TestClient) -> None:
    response = client.post(
        "/users", json={"username": "ann", "email": "ann@example.com"}
    )

    assert response.status_code == 201
    assert response.json() == {
        "id": 1,
        "username": "ann",
        "email": "ann@example.com",
        "role": "BA",
    }


def test_duplicate_email_returns_409(client: TestClient) -> None:
    body = {"username": "ann", "email": "ann@example.com"}
    client.post("/users", json=body)

    response = client.post("/users", json={**body, "username": "ann2"})

    assert response.status_code == 409


def test_invalid_role_and_email_return_422(client: TestClient) -> None:
    bad_role = client.post(
        "/users", json={"username": "a", "email": "a@example.com", "role": "CEO"}
    )
    bad_email = client.post("/users", json={"username": "a", "email": "not-an-email"})

    assert bad_role.status_code == 422
    assert bad_email.status_code == 422


def test_list_users_paginates_and_filters_by_email(client: TestClient) -> None:
    for name in ["a", "b", "c"]:
        client.post("/users", json={"username": name, "email": f"{name}@example.com"})

    first_page = client.get("/users", params={"page": 1, "pageSize": 2})
    second_page = client.get("/users", params={"page": 2, "pageSize": 2})
    by_email = client.get("/users", params={"email": "b@example.com"})

    assert [user["username"] for user in first_page.json()] == ["a", "b"]
    assert [user["username"] for user in second_page.json()] == ["c"]
    assert [user["username"] for user in by_email.json()] == ["b"]


def test_delete_user_then_404(client: TestClient) -> None:
    client.post("/users", json={"username": "ann", "email": "ann@example.com"})

    first = client.delete("/users/1")
    second = client.delete("/users/1")

    assert first.status_code == 204
    assert second.status_code == 404


def test_missing_identity_header_returns_401(client: TestClient) -> None:
    assert client.get("/projects").status_code == 401


def test_unregistered_email_returns_403(client: TestClient) -> None:
    response = client.get("/projects", headers={"X-User-Email": "ghost@example.com"})

    assert response.status_code == 403


def test_non_pm_cannot_create_project(client: TestClient) -> None:
    dev = register(client, "DEV")

    response = client.post(
        "/projects", json={"name": "Alpha", "description": "About"}, headers=dev
    )

    assert response.status_code == 403


def test_pm_creates_and_reads_project(client: TestClient) -> None:
    pm = register(client, "PM")

    project_id = create_project(client, pm)
    response = client.get(f"/projects/{project_id}", headers=pm)

    assert response.status_code == 200
    assert response.json()["name"] == "Alpha"
    assert response.json()["status"] == "NOT STARTED"


def test_unknown_project_returns_404(client: TestClient) -> None:
    pm = register(client, "PM")

    assert client.get("/projects/999", headers=pm).status_code == 404


def test_project_without_name_returns_422(client: TestClient) -> None:
    pm = register(client, "PM")

    response = client.post("/projects", json={"description": "About"}, headers=pm)

    assert response.status_code == 422


def test_duplicate_project_name_returns_409(client: TestClient) -> None:
    pm = register(client, "PM")
    create_project(client, pm)

    response = client.post(
        "/projects", json={"name": "Alpha", "description": "Again"}, headers=pm
    )

    assert response.status_code == 409


def test_list_projects_filters_by_status(client: TestClient) -> None:
    pm = register(client, "PM")
    create_project(client, pm, "Alpha")
    second = create_project(client, pm, "Beta")
    client.patch(f"/projects/{second}/status", json={"status": "DISCOVERY"}, headers=pm)

    response = client.get("/projects", params={"status": "DISCOVERY"}, headers=pm)

    assert [project["name"] for project in response.json()] == ["Beta"]


def test_project_status_follows_allowed_transitions(client: TestClient) -> None:
    pm = register(client, "PM")
    project_id = create_project(client, pm)

    allowed = client.patch(
        f"/projects/{project_id}/status", json={"status": "DISCOVERY"}, headers=pm
    )
    skipped = client.patch(
        f"/projects/{project_id}/status", json={"status": "COMPLETED"}, headers=pm
    )

    assert allowed.json()["status"] == "DISCOVERY"
    assert skipped.status_code == 409


def test_delete_project_removes_its_tasks(client: TestClient) -> None:
    pm = register(client, "PM")
    project_id = create_project(client, pm)
    task_id = create_task(client, pm, project_id)

    deleted = client.delete(f"/projects/{project_id}", headers=pm)
    task = client.get(f"/tasks/{task_id}", headers=pm)

    assert deleted.status_code == 204
    assert task.status_code == 404


def test_non_pm_cannot_delete_project(client: TestClient) -> None:
    pm = register(client, "PM")
    dev = register(client, "DEV")
    project_id = create_project(client, pm)

    assert client.delete(f"/projects/{project_id}", headers=dev).status_code == 403


def test_task_gets_reporter_and_defaults(client: TestClient) -> None:
    pm = register(client, "PM")
    dev = register(client, "DEV")
    project_id = create_project(client, pm)

    task_id = create_task(client, dev, project_id)
    task = client.get(f"/tasks/{task_id}", headers=dev).json()

    assert task["reporter_id"] == 2
    assert task["assignee_id"] is None
    assert task["status"] == "OPEN"
    assert task["story_points"] == 0


def test_task_for_unknown_project_returns_400(client: TestClient) -> None:
    dev = register(client, "DEV")

    response = client.post(
        "/tasks", json={"project_id": 999, "name": "Orphan"}, headers=dev
    )

    assert response.status_code == 400


def test_duplicate_task_name_in_project_returns_409(client: TestClient) -> None:
    pm = register(client, "PM")
    project_id = create_project(client, pm)
    create_task(client, pm, project_id)

    response = client.post(
        "/tasks", json={"project_id": project_id, "name": "Task 1"}, headers=pm
    )

    assert response.status_code == 409


def test_task_list_needs_project_and_filters_by_status(client: TestClient) -> None:
    pm = register(client, "PM")
    project_id = create_project(client, pm)
    create_task(client, pm, project_id, "Open one")
    started = create_task(client, pm, project_id, "Started one")
    client.patch(f"/tasks/{started}/status", json={"status": "IN PROGRESS"}, headers=pm)

    without_project = client.get("/tasks", headers=pm)
    started_only = client.get(
        "/tasks", params={"projectId": project_id, "status": "IN PROGRESS"}, headers=pm
    )

    assert without_project.status_code == 422
    assert [task["name"] for task in started_only.json()] == ["Started one"]


def test_assign_task_to_user_and_unknown_user(client: TestClient) -> None:
    pm = register(client, "PM")
    project_id = create_project(client, pm)
    task_id = create_task(client, pm, project_id)

    assigned = client.patch(
        f"/tasks/{task_id}/assign", json={"assignee_id": 1}, headers=pm
    )
    unknown_user = client.patch(
        f"/tasks/{task_id}/assign", json={"assignee_id": 999}, headers=pm
    )
    unknown_task = client.patch(
        "/tasks/999/assign", json={"assignee_id": 1}, headers=pm
    )

    assert assigned.json()["assignee_id"] == 1
    assert unknown_user.status_code == 400
    assert unknown_task.status_code == 404


def test_task_status_follows_allowed_transitions(client: TestClient) -> None:
    pm = register(client, "PM")
    project_id = create_project(client, pm)
    task_id = create_task(client, pm, project_id)

    allowed = client.patch(
        f"/tasks/{task_id}/status", json={"status": "IN PROGRESS"}, headers=pm
    )
    skipped = client.patch(
        f"/tasks/{task_id}/status", json={"status": "OPEN"}, headers=pm
    )

    assert allowed.json()["status"] == "IN PROGRESS"
    assert skipped.status_code == 409


def test_story_points_must_not_be_negative(client: TestClient) -> None:
    pm = register(client, "PM")
    project_id = create_project(client, pm)
    task_id = create_task(client, pm, project_id)

    valid = client.patch(
        f"/tasks/{task_id}/story-points", json={"story_points": 5}, headers=pm
    )
    negative = client.patch(
        f"/tasks/{task_id}/story-points", json={"story_points": -1}, headers=pm
    )

    assert valid.json()["story_points"] == 5
    assert negative.status_code == 422


def test_delete_task_then_404(client: TestClient) -> None:
    pm = register(client, "PM")
    project_id = create_project(client, pm)
    task_id = create_task(client, pm, project_id)

    first = client.delete(f"/tasks/{task_id}", headers=pm)
    second = client.delete(f"/tasks/{task_id}", headers=pm)

    assert first.status_code == 204
    assert second.status_code == 404


def test_only_pm_can_create_sprint(client: TestClient) -> None:
    pm = register(client, "PM")
    dev = register(client, "DEV")
    project_id = create_project(client, pm)
    body = {
        "project_id": project_id,
        "name": "Sprint 1",
        "start_date": "2026-01-01",
        "end_date": "2026-01-14",
        "max_capacity": 10,
    }

    assert client.post("/sprints", json=body, headers=dev).status_code == 403
    assert client.post("/sprints", json=body, headers=pm).status_code == 201


def test_sprint_needs_positive_capacity(client: TestClient) -> None:
    pm = register(client, "PM")
    project_id = create_project(client, pm)
    body = {
        "project_id": project_id,
        "name": "Sprint 1",
        "start_date": "2026-01-01",
        "end_date": "2026-01-14",
        "max_capacity": 0,
    }

    assert client.post("/sprints", json=body, headers=pm).status_code == 422


def test_add_task_within_capacity_updates_weight(client: TestClient) -> None:
    pm = register(client, "PM")
    project_id = create_project(client, pm)
    sprint_id = create_sprint(client, pm, project_id, max_capacity=10)
    task_id = create_task(client, pm, project_id)
    client.patch(f"/tasks/{task_id}/story-points", json={"story_points": 8}, headers=pm)

    added = client.patch(
        f"/sprints/{sprint_id}/add-task", json={"task_id": task_id}, headers=pm
    )
    weight = client.get(f"/sprints/{sprint_id}/current-weight", headers=pm)

    assert added.json()["sprint_id"] == sprint_id
    assert weight.json() == {"current_weight": 8}


def test_add_task_over_capacity_returns_409(client: TestClient) -> None:
    pm = register(client, "PM")
    project_id = create_project(client, pm)
    sprint_id = create_sprint(client, pm, project_id, max_capacity=10)
    first = create_task(client, pm, project_id, "First")
    second = create_task(client, pm, project_id, "Second")
    client.patch(f"/tasks/{first}/story-points", json={"story_points": 8}, headers=pm)
    client.patch(f"/tasks/{second}/story-points", json={"story_points": 5}, headers=pm)
    client.patch(f"/sprints/{sprint_id}/add-task", json={"task_id": first}, headers=pm)

    response = client.patch(
        f"/sprints/{sprint_id}/add-task", json={"task_id": second}, headers=pm
    )

    assert response.status_code == 409
    assert client.get(f"/tasks/{second}", headers=pm).json()["sprint_id"] is None


def test_add_unknown_task_or_sprint_returns_404(client: TestClient) -> None:
    pm = register(client, "PM")
    project_id = create_project(client, pm)
    sprint_id = create_sprint(client, pm, project_id)

    unknown_task = client.patch(
        f"/sprints/{sprint_id}/add-task", json={"task_id": 999}, headers=pm
    )
    unknown_sprint = client.patch(
        "/sprints/999/add-task", json={"task_id": 1}, headers=pm
    )

    assert unknown_task.status_code == 404
    assert unknown_sprint.status_code == 404


def test_sprint_status_cannot_skip_a_step(client: TestClient) -> None:
    pm = register(client, "PM")
    project_id = create_project(client, pm)
    sprint_id = create_sprint(client, pm, project_id)

    skipped = client.patch(
        f"/sprints/{sprint_id}/status", json={"status": "COMPLETED"}, headers=pm
    )
    allowed = client.patch(
        f"/sprints/{sprint_id}/status", json={"status": "ACTIVE"}, headers=pm
    )

    assert skipped.status_code == 409
    assert allowed.json()["status"] == "ACTIVE"


def test_completing_sprint_releases_only_unfinished_tasks(client: TestClient) -> None:
    pm = register(client, "PM")
    project_id = create_project(client, pm)
    sprint_id = create_sprint(client, pm, project_id)
    done = create_task(client, pm, project_id, "Done one")
    open_task = create_task(client, pm, project_id, "Open one")
    for task_id in [done, open_task]:
        client.patch(
            f"/sprints/{sprint_id}/add-task", json={"task_id": task_id}, headers=pm
        )
    client.patch(f"/tasks/{done}/status", json={"status": "IN PROGRESS"}, headers=pm)
    client.patch(f"/tasks/{done}/status", json={"status": "DONE"}, headers=pm)
    client.patch(f"/sprints/{sprint_id}/status", json={"status": "ACTIVE"}, headers=pm)

    client.patch(
        f"/sprints/{sprint_id}/status", json={"status": "COMPLETED"}, headers=pm
    )

    assert client.get(f"/tasks/{done}", headers=pm).json()["sprint_id"] == sprint_id
    assert client.get(f"/tasks/{open_task}", headers=pm).json()["sprint_id"] is None


def test_project_logs_record_every_change(client: TestClient) -> None:
    pm = register(client, "PM")
    project_id = create_project(client, pm)
    task_id = create_task(client, pm, project_id)
    client.patch(f"/tasks/{task_id}/status", json={"status": "IN PROGRESS"}, headers=pm)
    client.delete(f"/tasks/{task_id}", headers=pm)

    logs = client.get(f"/projects/{project_id}/logs", headers=pm).json()

    summary = [(log["subject_type"], log["action_type"]) for log in logs]
    assert summary == [
        ("TASK", "DELETE"),
        ("TASK", "UPDATE"),
        ("TASK", "CREATE"),
        ("PROJECT", "CREATE"),
    ]
    assert logs[-1]["actor_id"] == 1
    assert logs[1]["change_record"]["status"] == "IN PROGRESS"


def test_failed_request_writes_no_log(client: TestClient) -> None:
    pm = register(client, "PM")
    project_id = create_project(client, pm)
    client.patch(
        f"/projects/{project_id}/status", json={"status": "COMPLETED"}, headers=pm
    )

    logs = client.get(f"/projects/{project_id}/logs", headers=pm).json()

    assert len(logs) == 1


def test_logs_for_unknown_project_return_404(client: TestClient) -> None:
    pm = register(client, "PM")

    assert client.get("/projects/999/logs", headers=pm).status_code == 404


def test_sprint_report_shows_current_capacity(client: TestClient) -> None:
    pm = register(client, "PM")
    project_id = create_project(client, pm)
    full = create_sprint(client, pm, project_id, max_capacity=10)
    empty = create_sprint(client, pm, project_id, max_capacity=5)
    task_id = create_task(client, pm, project_id)
    client.patch(f"/tasks/{task_id}/story-points", json={"story_points": 3}, headers=pm)
    client.patch(f"/sprints/{full}/add-task", json={"task_id": task_id}, headers=pm)

    report = client.get(f"/projects/{project_id}/sprint-report", headers=pm).json()

    assert [(row["id"], row["current_capacity"]) for row in report] == [
        (full, 3),
        (empty, 0),
    ]


def test_workload_report_groups_by_status_and_user(client: TestClient) -> None:
    pm = register(client, "PM")
    project_id = create_project(client, pm)
    for name in ["One", "Two"]:
        task_id = create_task(client, pm, project_id, name, assignee_id=1)
    client.patch(f"/tasks/{task_id}/status", json={"status": "IN PROGRESS"}, headers=pm)

    response = client.get(f"/projects/{project_id}/workload-report", headers=pm)

    assert response.json() == {
        "project_id": project_id,
        "workload_report": {
            "IN PROGRESS": [{"id": 1, "username": "pm", "task_count": 1}],
            "OPEN": [{"id": 1, "username": "pm", "task_count": 1}],
        },
    }


def test_reports_for_project_without_tasks_are_empty(client: TestClient) -> None:
    pm = register(client, "PM")
    project_id = create_project(client, pm)

    workload = client.get(f"/projects/{project_id}/workload-report", headers=pm)
    sprints = client.get(f"/projects/{project_id}/sprint-report", headers=pm)
    unknown = client.get("/projects/999/workload-report", headers=pm)

    assert workload.json()["workload_report"] == {}
    assert sprints.json() == []
    assert unknown.status_code == 404


def test_parallel_add_task_never_exceeds_capacity(client: TestClient) -> None:
    pm = register(client, "PM")
    project_id = create_project(client, pm)
    sprint_id = create_sprint(client, pm, project_id, max_capacity=5)
    task_ids = []
    for number in range(20):
        task_id = create_task(client, pm, project_id, f"Task {number}")
        client.patch(
            f"/tasks/{task_id}/story-points", json={"story_points": 1}, headers=pm
        )
        task_ids.append(task_id)

    def add_to_sprint(task_id: int) -> int:
        response = client.patch(
            f"/sprints/{sprint_id}/add-task", json={"task_id": task_id}, headers=pm
        )
        return int(response.status_code)

    with ThreadPoolExecutor(max_workers=20) as pool:
        statuses = list(pool.map(add_to_sprint, task_ids))

    weight = client.get(f"/sprints/{sprint_id}/current-weight", headers=pm).json()
    assert weight["current_weight"] == 5
    assert statuses.count(200) == 5
    assert statuses.count(409) == 15


def test_conflicting_status_changes_allow_only_one_winner(client: TestClient) -> None:
    pm = register(client, "PM")
    project_id = create_project(client, pm)
    task_ids = []
    for number in range(10):
        task_id = create_task(client, pm, project_id, f"Task {number}")
        client.patch(
            f"/tasks/{task_id}/status", json={"status": "IN PROGRESS"}, headers=pm
        )
        task_ids.append(task_id)
    changes = []
    for task_id in task_ids:
        changes.append((task_id, "DONE"))
        changes.append((task_id, "VOID"))

    def change_status(change: tuple[int, str]) -> tuple[int, int]:
        task_id, status = change
        response = client.patch(
            f"/tasks/{task_id}/status", json={"status": status}, headers=pm
        )
        return task_id, response.status_code

    with ThreadPoolExecutor(max_workers=20) as pool:
        results = list(pool.map(change_status, changes))

    successes_per_task = {task_id: 0 for task_id in task_ids}
    for task_id, code in results:
        if code == 200:
            successes_per_task[task_id] += 1
    logs = client.get(f"/projects/{project_id}/logs", headers=pm).json()
    updates_per_task = {task_id: 0 for task_id in task_ids}
    for log in logs:
        if log["subject_type"] == "TASK" and log["action_type"] == "UPDATE":
            updates_per_task[log["subject_id"]] += 1

    assert list(successes_per_task.values()) == [1] * 10
    assert list(updates_per_task.values()) == [2] * 10
