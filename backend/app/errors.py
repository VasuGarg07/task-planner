from fastapi import HTTPException


def found_or_404[T](item: T | None, name: str) -> T:
    if item is None:
        raise HTTPException(status_code=404, detail=f"{name} not found")
    return item


def check_transition[S: str](allowed: dict[S, list[S]], current: S, target: S) -> None:
    if target not in allowed[current]:
        raise HTTPException(
            status_code=409, detail=f"Cannot change status from {current} to {target}"
        )
