from dataclasses import dataclass

from .operation import Operation


@dataclass
class Log:
    term: int
    index: int
    operation: Operation
