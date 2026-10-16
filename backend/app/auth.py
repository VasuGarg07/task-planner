from typing import Annotated

from fastapi import Depends, Header, HTTPException

from app.database import DbConn
from app.models import User
from app.repository import users


def current_user(
    conn: DbConn, x_user_email: Annotated[str | None, Header()] = None
) -> User:
    if x_user_email is None:
        raise HTTPException(status_code=401, detail="Missing X-User-Email header")
    user = users.find_user_by_email(conn, x_user_email)
    if user is None:
        raise HTTPException(status_code=403, detail="User is not registered")
    return user


CurrentUser = Annotated[User, Depends(current_user)]


def require_pm(user: CurrentUser) -> User:
    if user.role != "PM":
        raise HTTPException(status_code=403, detail="Only a PM can do this")
    return user


PmUser = Annotated[User, Depends(require_pm)]
