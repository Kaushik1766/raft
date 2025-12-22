import time
from typing import List
from dataclasses import dataclass, field
import asyncio


from .log import Log


peer_ports = []
heartbeat_interval = 50


@dataclass
class RaftNode:
    id: str
    delay: int  # in ms
    port: int
    is_leader: bool = False
    logs: List[Log] = field(default_factory=list)
    last_hearbeat: float = field(default=time.time(), init=False)

    async def __post_init__(self):
        if self.delay < heartbeat_interval:
            raise ValueError("Delay must be greater than heartbeat interval")

        self.heartbeat_task = asyncio.create_task(self.send_heartbeat())
        self.check_leader_task = asyncio.create_task(self.check_leader())

    def __del__(self):
        self.heartbeat_task.cancel()
        self.check_leader_task.cancel()

    def get_votes(self):
        """
        get votes from all peers
        """
        pass

    async def send_heartbeat(self):
        """
        send heartbeat to all peers
        """
        while True:
            for i in peer_ports:
                if i != self.port:
                    # send heartbeat to /listen
                    pass
            await asyncio.sleep(heartbeat_interval)

    async def check_leader(self):
        """
        check if leader is alive
        """
        while True:
            if not self.is_leader and self.last_hearbeat + self.delay < time.time():
                # perform leader election
                self.get_votes()

            await asyncio.sleep(self.delay)

    @property
    def term(self):
        """
        get last term from logs
        """
        return self.logs[-1].term

    @property
    def index(self):
        """
        get last index from logs
        """
        return self.logs[-1].index
