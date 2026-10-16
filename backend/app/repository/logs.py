from psycopg.types.json import Jsonb
from pydantic import BaseModel

from app.database import Connection, fetch_all
from app.models import ActionType, Log, SubjectType


def add_log(
    conn: Connection,
    actor_id: int,
    subject_type: SubjectType,
    subject_id: int,
    project_id: int,
    action_type: ActionType,
    record: BaseModel,
) -> None:
    conn.execute(
        """
        INSERT INTO logs
            (project_id, actor_id, subject_type, subject_id, action_type, change_record)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (
            project_id,
            actor_id,
            subject_type,
            subject_id,
            action_type,
            Jsonb(record.model_dump(mode="json")),
        ),
    )


def list_logs(conn: Connection, project_id: int) -> list[Log]:
    return fetch_all(
        conn,
        Log,
        """
        SELECT id, created_at, project_id, actor_id, subject_type, subject_id,
               action_type, change_record
        FROM logs WHERE project_id = %s ORDER BY id DESC
        """,
        (project_id,),
    )
