from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from app.auth import CurrentUser, current_user
from app.database import DbConn
from app.errors import check_transition, found_or_404
from app.models import (
    NewTask,
    Task,
    TaskAssignment,
    TaskStatus,
    TaskStatusChange,
    TaskStoryPoints,
)
from app.pagination import PageQuery
from app.repository import logs
from app.repository import tasks as repo

router = APIRouter(
    prefix="/tasks", tags=["tasks"], dependencies=[Depends(current_user)]
)

TASK_TRANSITIONS: dict[TaskStatus, list[TaskStatus]] = {
    "OPEN": ["IN PROGRESS", "ON HOLD", "VOID"],
    "IN PROGRESS": ["ON HOLD", "DONE", "VOID"],
    "ON HOLD": ["OPEN", "IN PROGRESS", "VOID"],
    "DONE": ["OPEN"],
    "VOID": [],
}


@router.post("", status_code=201)
def post_task(task: NewTask, conn: DbConn, user: CurrentUser) -> Task:
    created = repo.create_task(conn, task, user.id)
    logs.add_log(
        conn, user.id, "TASK", created.id, created.project_id, "CREATE", created
    )
    return created


@router.get("")
def get_tasks(
    conn: DbConn,
    page: PageQuery,
    project_id: Annotated[int, Query(alias="projectId")],
    status: TaskStatus | None = None,
) -> list[Task]:
    return repo.list_tasks(conn, project_id, status, page.limit, page.offset)


@router.get("/{task_id}")
def get_task(task_id: int, conn: DbConn) -> Task:
    return found_or_404(repo.find_task(conn, task_id), "Task")


@router.delete("/{task_id}", status_code=204)
def remove_task(task_id: int, conn: DbConn, user: CurrentUser) -> None:
    deleted = found_or_404(repo.delete_task(conn, task_id), "Task")
    logs.add_log(
        conn, user.id, "TASK", deleted.id, deleted.project_id, "DELETE", deleted
    )


@router.patch("/{task_id}/assign")
def patch_task_assignee(
    task_id: int, body: TaskAssignment, conn: DbConn, user: CurrentUser
) -> Task:
    updated = found_or_404(repo.set_assignee(conn, task_id, body.assignee_id), "Task")
    logs.add_log(conn, user.id, "TASK", task_id, updated.project_id, "UPDATE", updated)
    return updated


@router.patch("/{task_id}/status")
def patch_task_status(
    task_id: int, change: TaskStatusChange, conn: DbConn, user: CurrentUser
) -> Task:
    task = found_or_404(repo.find_task(conn, task_id), "Task")
    check_transition(TASK_TRANSITIONS, task.status, change.status)
    updated = repo.set_task_status(conn, task_id, task.status, change.status)
    if updated is None:
        raise HTTPException(status_code=409, detail="Task status changed meanwhile")
    logs.add_log(conn, user.id, "TASK", task_id, updated.project_id, "UPDATE", updated)
    return updated


@router.patch("/{task_id}/story-points")
def patch_task_story_points(
    task_id: int, body: TaskStoryPoints, conn: DbConn, user: CurrentUser
) -> Task:
    updated = found_or_404(
        repo.set_story_points(conn, task_id, body.story_points), "Task"
    )
    logs.add_log(conn, user.id, "TASK", task_id, updated.project_id, "UPDATE", updated)
    return updated
