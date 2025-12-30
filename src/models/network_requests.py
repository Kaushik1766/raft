from enum import Enum

from pydantic import BaseModel

from .log import Log


class RequestType(Enum):
    HEARTBEAT = 1
    APPEND_LOG = 2
    COMMIT_LOG = 3
    GET_VOTE = 4


class HeartBeat(BaseModel):
    type: RequestType


class AppendLog(BaseModel):
    type: RequestType
    data: Log


class CommitLog(BaseModel):
    type: RequestType
    index: int


class GetVote(BaseModel):
    type: RequestType
    index: int
    term: int