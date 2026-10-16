from fastapi import APIRouter, Depends, HTTPException

from app.auth import PmUser, current_user
from app.database import DbConn
from app.errors import check_transition, found_or_404
from app.models import (
    NewSprint,
    Sprint,
    SprintStatus,
    SprintStatusChange,
    SprintTask,
    SprintWeight,
    Task,
)
from app.repository import logs, tasks
from app.repository import sprints as repo

router = APIRouter(
    prefix="/sprints", tags=["sprints"], dependencies=[Depends(current_user)]
)

SPRINT_TRANSITIONS: dict[SprintStatus, list[SprintStatus]] = {
    "PLANNING": ["ACTIVE"],
    "ACTIVE": ["COMPLETED"],
    "COMPLETED": [],
}


@router.post("", status_code=201)
def post_sprint(sprint: NewSprint, conn: DbConn, pm: PmUser) -> Sprint:
    created = repo.create_sprint(conn, sprint)
    logs.add_log(
        conn, pm.id, "SPRINT", created.id, created.project_id, "CREATE", created
    )
    return created


@router.get("/{sprint_id}")
def get_sprint(sprint_id: int, conn: DbConn) -> Sprint:
    return found_or_404(repo.find_sprint(conn, sprint_id), "Sprint")


@router.get("/{sprint_id}/current-weight")
def get_sprint_weight(sprint_id: int, conn: DbConn) -> SprintWeight:
    found_or_404(repo.find_sprint(conn, sprint_id), "Sprint")
    return repo.sprint_weight(conn, sprint_id)


@router.patch("/{sprint_id}/add-task")
def add_task_to_sprint(
    sprint_id: int, body: SprintTask, conn: DbConn, pm: PmUser
) -> Task:
    sprint = found_or_404(repo.find_sprint(conn, sprint_id), "Sprint")
    task = found_or_404(tasks.find_task(conn, body.task_id), "Task")
    weight = repo.sprint_weight(conn, sprint_id)
    if weight.current_weight + task.story_points > sprint.max_capacity:
        raise HTTPException(status_code=409, detail="Sprint is over capacity")
    updated = found_or_404(tasks.set_task_sprint(conn, task.id, sprint_id), "Task")
    logs.add_log(conn, pm.id, "SPRINT", sprint_id, sprint.project_id, "UPDATE", updated)
    return updated


@router.patch("/{sprint_id}/status")
def patch_sprint_status(
    sprint_id: int, change: SprintStatusChange, conn: DbConn, pm: PmUser
) -> Sprint:
    sprint = found_or_404(repo.find_sprint(conn, sprint_id), "Sprint")
    check_transition(SPRINT_TRANSITIONS, sprint.status, change.status)
    updated = found_or_404(
        repo.set_sprint_status(conn, sprint_id, change.status), "Sprint"
    )
    if change.status == "COMPLETED":
        repo.release_unfinished_tasks(conn, sprint_id)
    logs.add_log(conn, pm.id, "SPRINT", sprint_id, sprint.project_id, "UPDATE", updated)
    return updated
