from app.database import Connection, fetch_all, fetch_one, find_one
from app.models import NewProject, Project, ProjectStatus

PROJECT_COLUMNS = "id, name, description, created_at, status"


def create_project(conn: Connection, project: NewProject) -> Project:
    return fetch_one(
        conn,
        Project,
        f"INSERT INTO projects (name, description) VALUES (%s, %s) RETURNING {PROJECT_COLUMNS}",
        (project.name, project.description),
    )


def find_project(conn: Connection, project_id: int) -> Project | None:
    return find_one(
        conn,
        Project,
        f"SELECT {PROJECT_COLUMNS} FROM projects WHERE id = %s",
        (project_id,),
    )


def list_projects(
    conn: Connection, status: ProjectStatus | None, limit: int, offset: int
) -> list[Project]:
    return fetch_all(
        conn,
        Project,
        f"""
        SELECT {PROJECT_COLUMNS} FROM projects
        WHERE (%(status)s::text IS NULL OR status = %(status)s)
        ORDER BY id LIMIT %(limit)s OFFSET %(offset)s
        """,
        {"status": status, "limit": limit, "offset": offset},
    )


def delete_project(conn: Connection, project_id: int) -> Project | None:
    return find_one(
        conn,
        Project,
        f"DELETE FROM projects WHERE id = %s RETURNING {PROJECT_COLUMNS}",
        (project_id,),
    )


def set_project_status(
    conn: Connection, project_id: int, status: ProjectStatus
) -> Project | None:
    return find_one(
        conn,
        Project,
        f"UPDATE projects SET status = %s WHERE id = %s RETURNING {PROJECT_COLUMNS}",
        (status, project_id),
    )
