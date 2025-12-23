import time
from typing import List
from dataclasses import dataclass, field
import asyncio
import aiohttp

from .operation import Operation


from .log import Log


peer_ports = [3000, 3001, 3002, 3003, 3004]
heartbeat_interval = 50


@dataclass
class RaftNode:
    id: str
    delay: int  # in ms
    port: int
    is_leader: bool = field(default=False)
    logs: List[Log] = field(
        default_factory=lambda: [
            Log(index=0, term=0, operation=Operation(opcode=0, data="nil"))
        ]
    )
    last_hearbeat: float = field(default=time.time(), init=False)

    def __post_init__(self):
        if self.delay < heartbeat_interval:
            raise ValueError("Delay must be greater than heartbeat interval")

    async def start(self):
        self.session = aiohttp.ClientSession()
        self.heartbeat_task = asyncio.create_task(self.send_heartbeat())
        self.check_leader_task = asyncio.create_task(self.check_leader())

    def receive_heartbeat(self):
        self.last_hearbeat = time.time()

    async def stop(self):
        self.heartbeat_task.cancel()
        self.check_leader_task.cancel()

    async def get_votes(self):
        """
        get votes from all peers
        """
        tasks = []
        for i in peer_ports:
            if i != self.port:
                tasks.append(self.session.get(f"http://localhost:{i}/vote"))

        res = await asyncio.gather(*tasks)
        print(res)
        for i in res:
            print(await i.text())

    def vote(self, term: int, index: int) -> bool:
        if term > self.term and index >= self.index:
            return True
        else:
            return False

    async def send_heartbeat(self):
        """
        send heartbeat to all peers
        """
        while True:
            if self.is_leader:
                for i in peer_ports:
                    if i != self.port:
                        # send heartbeat to /listen
                        pass
            await asyncio.sleep(heartbeat_interval / 1000)

    async def check_leader(self):
        """
        check if leader is alive
        """
        while True:
            # print(
            #     f"Last heartbeat: {self.last_hearbeat}, Current time: {time.time()}, check: {self.last_hearbeat + self.delay} "
            # )
            if (
                not self.is_leader
                and self.last_hearbeat + self.delay / 1000 < time.time()
            ):
                # perform leader election
                await self.get_votes()

            await asyncio.sleep(self.delay / 1000)

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
