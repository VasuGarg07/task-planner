from fastapi import APIRouter

from app.database import DbConn
from app.errors import found_or_404
from app.models import NewUser, User
from app.pagination import PageQuery
from app.repository import users as repo

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", status_code=201)
def post_user(user: NewUser, conn: DbConn) -> User:
    return repo.create_user(conn, user)


@router.get("")
def get_users(conn: DbConn, page: PageQuery, email: str | None = None) -> list[User]:
    return repo.list_users(conn, email, page.limit, page.offset)


@router.delete("/{user_id}", status_code=204)
def remove_user(user_id: int, conn: DbConn) -> None:
    found_or_404(repo.delete_user(conn, user_id), "User")
