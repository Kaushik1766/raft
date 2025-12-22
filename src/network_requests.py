from dataclasses import dataclass
from enum import Enum
from typing import TypedDict

from .log import Log


class RequestType(Enum):
    HEARTBEAT = 1
    APPEND_LOG = 2
    COMMIT_LOG = 3


@dataclass
class HeartBeat(TypedDict):
    type: RequestType


@dataclass
class AppendLog(TypedDict):
    type: RequestType
    data: Log


@dataclass
class CommitLog(TypedDict):
    type: RequestType
    index: int
