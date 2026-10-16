from app.database import Connection, fetch_all, fetch_one, find_one
from app.models import NewTask, Task, TaskStatus, WorkloadEntry, WorkloadRow

TASK_COLUMNS = """
    id, project_id, name, description, reporter AS reporter_id,
    assignee AS assignee_id, created_at, status, sprint_id, story_points
"""


def create_task(conn: Connection, task: NewTask, reporter_id: int) -> Task:
    return fetch_one(
        conn,
        Task,
        f"""
        INSERT INTO tasks (project_id, name, description, reporter, assignee)
        VALUES (%s, %s, %s, %s, %s) RETURNING {TASK_COLUMNS}
        """,
        (task.project_id, task.name, task.description, reporter_id, task.assignee_id),
    )


def find_task(conn: Connection, task_id: int) -> Task | None:
    return find_one(
        conn, Task, f"SELECT {TASK_COLUMNS} FROM tasks WHERE id = %s", (task_id,)
    )


def list_tasks(
    conn: Connection,
    project_id: int,
    status: TaskStatus | None,
    limit: int,
    offset: int,
) -> list[Task]:
    return fetch_all(
        conn,
        Task,
        f"""
        SELECT {TASK_COLUMNS} FROM tasks
        WHERE project_id = %(project_id)s
        AND (%(status)s::text IS NULL OR status = %(status)s)
        ORDER BY id LIMIT %(limit)s OFFSET %(offset)s
        """,
        {"project_id": project_id, "status": status, "limit": limit, "offset": offset},
    )


def delete_task(conn: Connection, task_id: int) -> Task | None:
    return find_one(
        conn,
        Task,
        f"DELETE FROM tasks WHERE id = %s RETURNING {TASK_COLUMNS}",
        (task_id,),
    )


def set_assignee(conn: Connection, task_id: int, assignee_id: int) -> Task | None:
    return find_one(
        conn,
        Task,
        f"UPDATE tasks SET assignee = %s WHERE id = %s RETURNING {TASK_COLUMNS}",
        (assignee_id, task_id),
    )


def set_task_status(
    conn: Connection, task_id: int, current: TaskStatus, status: TaskStatus
) -> Task | None:
    return find_one(
        conn,
        Task,
        f"""
        UPDATE tasks SET status = %s WHERE id = %s AND status = %s
        RETURNING {TASK_COLUMNS}
        """,
        (status, task_id, current),
    )


def set_story_points(conn: Connection, task_id: int, story_points: int) -> Task | None:
    return find_one(
        conn,
        Task,
        f"UPDATE tasks SET story_points = %s WHERE id = %s RETURNING {TASK_COLUMNS}",
        (story_points, task_id),
    )


def set_task_sprint(conn: Connection, task_id: int, sprint_id: int) -> Task | None:
    return find_one(
        conn,
        Task,
        f"UPDATE tasks SET sprint_id = %s WHERE id = %s RETURNING {TASK_COLUMNS}",
        (sprint_id, task_id),
    )


def workload_report(
    conn: Connection, project_id: int
) -> dict[str, list[WorkloadEntry]]:
    rows = fetch_all(
        conn,
        WorkloadRow,
        """
        SELECT t.status, u.id, u.username, COUNT(*) AS task_count
        FROM tasks t JOIN users u ON t.assignee = u.id
        WHERE t.project_id = %s
        GROUP BY t.status, u.id, u.username
        ORDER BY t.status, u.id
        """,
        (project_id,),
    )
    report: dict[str, list[WorkloadEntry]] = {}
    for row in rows:
        entry = WorkloadEntry(
            id=row.id, username=row.username, task_count=row.task_count
        )
        report.setdefault(row.status, []).append(entry)
    return report
