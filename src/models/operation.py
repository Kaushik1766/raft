from pydantic import BaseModel


class Operation(BaseModel):
    opcode: int
    data: str

    def commit(self):
        raise NotImplementedError