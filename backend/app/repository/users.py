from app.database import Connection, fetch_all, fetch_one, find_one
from app.models import NewUser, User

USER_COLUMNS = "id, username, email, role"


def create_user(conn: Connection, user: NewUser) -> User:
    return fetch_one(
        conn,
        User,
        f"INSERT INTO users (username, email, role) VALUES (%s, %s, %s) RETURNING {USER_COLUMNS}",
        (user.username, user.email, user.role),
    )


def find_user_by_email(conn: Connection, email: str) -> User | None:
    return find_one(
        conn, User, f"SELECT {USER_COLUMNS} FROM users WHERE email = %s", (email,)
    )


def list_users(
    conn: Connection, email: str | None, limit: int, offset: int
) -> list[User]:
    return fetch_all(
        conn,
        User,
        f"""
        SELECT {USER_COLUMNS} FROM users
        WHERE (%(email)s::text IS NULL OR email = %(email)s)
        ORDER BY id LIMIT %(limit)s OFFSET %(offset)s
        """,
        {"email": email, "limit": limit, "offset": offset},
    )


def delete_user(conn: Connection, user_id: int) -> User | None:
    return find_one(
        conn,
        User,
        f"DELETE FROM users WHERE id = %s RETURNING {USER_COLUMNS}",
        (user_id,),
    )
