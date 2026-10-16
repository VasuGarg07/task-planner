from app.database import Connection, fetch_all, fetch_one, find_one
from app.models import NewSprint, Sprint, SprintLoad, SprintStatus, SprintWeight

SPRINT_COLUMNS = "id, project_id, name, start_date, end_date, max_capacity, status"


def create_sprint(conn: Connection, sprint: NewSprint) -> Sprint:
    return fetch_one(
        conn,
        Sprint,
        f"""
        INSERT INTO sprints (project_id, name, start_date, end_date, max_capacity)
        VALUES (%s, %s, %s, %s, %s) RETURNING {SPRINT_COLUMNS}
        """,
        (
            sprint.project_id,
            sprint.name,
            sprint.start_date,
            sprint.end_date,
            sprint.max_capacity,
        ),
    )


def find_sprint(conn: Connection, sprint_id: int) -> Sprint | None:
    return find_one(
        conn,
        Sprint,
        f"SELECT {SPRINT_COLUMNS} FROM sprints WHERE id = %s",
        (sprint_id,),
    )


def set_sprint_status(
    conn: Connection, sprint_id: int, status: SprintStatus
) -> Sprint | None:
    return find_one(
        conn,
        Sprint,
        f"UPDATE sprints SET status = %s WHERE id = %s RETURNING {SPRINT_COLUMNS}",
        (status, sprint_id),
    )


def release_unfinished_tasks(conn: Connection, sprint_id: int) -> None:
    conn.execute(
        """
        UPDATE tasks SET sprint_id = NULL
        WHERE sprint_id = %s AND status NOT IN ('DONE', 'VOID')
        """,
        (sprint_id,),
    )


def sprint_weight(conn: Connection, sprint_id: int) -> SprintWeight:
    return fetch_one(
        conn,
        SprintWeight,
        "SELECT COALESCE(SUM(story_points), 0) AS current_weight FROM tasks WHERE sprint_id = %s",
        (sprint_id,),
    )


def list_sprint_loads(conn: Connection, project_id: int) -> list[SprintLoad]:
    return fetch_all(
        conn,
        SprintLoad,
        """
        SELECT s.id, s.project_id, s.name, s.start_date, s.end_date,
               s.max_capacity, s.status,
               COALESCE(SUM(t.story_points), 0) AS current_capacity
        FROM sprints s LEFT JOIN tasks t ON t.sprint_id = s.id
        WHERE s.project_id = %s
        GROUP BY s.id ORDER BY s.id
        """,
        (project_id,),
    )


def lock_sprint(conn: Connection, sprint_id: int) -> Sprint | None:
    return find_one(
        conn,
        Sprint,
        f"SELECT {SPRINT_COLUMNS} FROM sprints WHERE id = %s FOR UPDATE",
        (sprint_id,),
    )
