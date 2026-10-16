from typing import Annotated

from fastapi import Depends, Query


class Page:
    def __init__(
        self,
        page: Annotated[int, Query(ge=1)] = 1,
        page_size: Annotated[int, Query(alias="pageSize", ge=1, le=100)] = 10,
    ) -> None:
        self.limit = page_size
        self.offset = (page - 1) * page_size


PageQuery = Annotated[Page, Depends()]
