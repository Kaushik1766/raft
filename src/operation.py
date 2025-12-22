from dataclasses import dataclass


@dataclass
class Operation:
    opcode: int
    data: str

    def commit(self):
        raise NotImplementedError
