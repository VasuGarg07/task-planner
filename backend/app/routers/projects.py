from fastapi import APIRouter, Depends

from app.auth import PmUser, current_user, require_pm
from app.database import DbConn
from app.errors import check_transition, found_or_404
from app.models import (
    Log,
    NewProject,
    Project,
    ProjectStatus,
    ProjectStatusChange,
    SprintLoad,
    WorkloadReport,
)
from app.pagination import PageQuery
from app.repository import logs, sprints, tasks
from app.repository import projects as repo

router = APIRouter(
    prefix="/projects", tags=["projects"], dependencies=[Depends(current_user)]
)

PROJECT_TRANSITIONS: dict[ProjectStatus, list[ProjectStatus]] = {
    "NOT STARTED": ["DISCOVERY", "DROPPED"],
    "DISCOVERY": ["IN PROGRESS", "ON HOLD", "DROPPED"],
    "IN PROGRESS": ["ON HOLD", "COMPLETED", "DROPPED"],
    "ON HOLD": ["IN PROGRESS", "DISCOVERY", "DROPPED"],
    "COMPLETED": [],
    "DROPPED": [],
}


@router.post("", status_code=201)
def post_project(project: NewProject, conn: DbConn, pm: PmUser) -> Project:
    created = repo.create_project(conn, project)
    logs.add_log(conn, pm.id, "PROJECT", created.id, created.id, "CREATE", created)
    return created


@router.get("")
def get_projects(
    conn: DbConn, page: PageQuery, status: ProjectStatus | None = None
) -> list[Project]:
    return repo.list_projects(conn, status, page.limit, page.offset)


@router.get("/{project_id}")
def get_project(project_id: int, conn: DbConn) -> Project:
    return found_or_404(repo.find_project(conn, project_id), "Project")


@router.delete("/{project_id}", status_code=204, dependencies=[Depends(require_pm)])
def remove_project(project_id: int, conn: DbConn) -> None:
    found_or_404(repo.delete_project(conn, project_id), "Project")


@router.patch("/{project_id}/status")
def patch_project_status(
    project_id: int, change: ProjectStatusChange, conn: DbConn, pm: PmUser
) -> Project:
    project = found_or_404(repo.find_project(conn, project_id), "Project")
    check_transition(PROJECT_TRANSITIONS, project.status, change.status)
    updated = found_or_404(
        repo.set_project_status(conn, project_id, change.status), "Project"
    )
    logs.add_log(conn, pm.id, "PROJECT", project_id, project_id, "UPDATE", updated)
    return updated


@router.get("/{project_id}/logs")
def get_project_logs(project_id: int, conn: DbConn) -> list[Log]:
    found_or_404(repo.find_project(conn, project_id), "Project")
    return logs.list_logs(conn, project_id)


@router.get("/{project_id}/sprint-report")
def get_sprint_report(project_id: int, conn: DbConn) -> list[SprintLoad]:
    found_or_404(repo.find_project(conn, project_id), "Project")
    return sprints.list_sprint_loads(conn, project_id)


@router.get("/{project_id}/workload-report")
def get_workload_report(project_id: int, conn: DbConn) -> WorkloadReport:
    found_or_404(repo.find_project(conn, project_id), "Project")
    return WorkloadReport(
        project_id=project_id,
        workload_report=tasks.workload_report(conn, project_id),
    )
