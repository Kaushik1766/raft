from pydantic import BaseModel

from .operation import Operation


class Log(BaseModel):
    term: int
    index: int
    operation: Operation