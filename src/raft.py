import asyncio
import os
import signal
import time
from asyncio.tasks import Task
from dataclasses import dataclass, field
from types import FunctionType
from typing import List

import aiohttp
from aiohttp.client import ClientSession

from .log import Log
from .operation import Operation

peer_ports = [i for i in range(3000, 3005)]
heartbeat_interval = 100


def updates_heartbeat(func: FunctionType):
    def wrapper(self, *args, **kwargs):
        self.last_hearbeat = time.time()
        # print(f"{self.id} received heartbeat")
        return func(self, *args, **kwargs)

    return wrapper


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
    current_term: int = field(default=0, init=False)
    voted_for_term: int = field(default=0, init=False)

    def __post_init__(self):
        if self.delay < heartbeat_interval:
            raise ValueError("Delay must be greater than heartbeat interval")

    async def start(self):
        self.session = aiohttp.ClientSession()
        self.heartbeat_task = asyncio.create_task(self.send_heartbeat())
        self.check_leader_task = asyncio.create_task(self.check_leader())

    @updates_heartbeat
    def receive_heartbeat(self):
        pass
        # self.last_hearbeat = time.time()

    async def stop(self):
        await self.session.close()
        self.heartbeat_task.cancel()
        self.check_leader_task.cancel()

    async def get_votes(self):
        """
        get votes from all peers
        """

        async def fetch_vote(session: ClientSession, port: int):
            try:
                async with session.get(
                    url=f"http://localhost:{port}/vote",
                    params={
                        "term": self.current_term,
                        "index": self.index,
                        "id": self.id,
                    },
                ) as response:
                    return await response.json()
            except Exception:
                print(f"Error fetching vote from {port}")
                return None

        tasks: List[Task] = []
        self.current_term += 1
        self.voted_for_term = self.current_term
        for i in peer_ports:
            if i != self.port:
                tasks.append(asyncio.create_task(fetch_vote(self.session, i)))

        res = await asyncio.gather(*tasks)
        votes = []
        for i in res:
            if i is not None:
                votes.append(i['vote'])

        if sum(votes) + 1 > len(peer_ports) // 2:
            self.is_leader = True
            print(f"Node {self.id} became the leader for term {self.current_term}")
        elif len(votes)+1<=len(peer_ports)//2:
            print("More than half nodes are down, shutting down....")
            os.kill(os.getpid(), signal.SIGTERM)
        else:
            # self.current_term -= 1
            print(f"{self.id} cant get quorum")

    @updates_heartbeat # updating so it doesnt start election
    def vote(self, term: int, index: int, id: str) -> bool:
        if term > self.current_term and index >= self.index and self.voted_for_term < term:
            self.current_term = term
            self.voted_for_term = term
            # self.is_leader = False
            print(f"{self.id} voted for {id} in term {term}")
            return True
        else:
            print(f"{self.id} rejected request of {id} in term {term}")
            return False

    async def send_heartbeat(self):
        """
        send heartbeat to all peers
        """

        async def heartbeat_request(session: ClientSession, port: int):
            try:
                async with session.post(
                    f"http://localhost:{port}/heartbeat"
                ) as response:
                    return response.status
            except Exception:
                # print(f"node on port {port} is unreachable")
                return None

        while True:
            tasks: List[Task] = []
            if self.is_leader:
                for i in peer_ports:
                    if i != self.port:
                        tasks.append(
                            asyncio.create_task(heartbeat_request(self.session, i))
                        )
                await asyncio.gather(*tasks)
            await asyncio.sleep(heartbeat_interval / 1000)

    async def check_leader(self):
        """
        check if leader is alive
        """
        while True:
            if (
                not self.is_leader
                and self.last_hearbeat + self.delay / 1000 < time.time()
            ):
                # perform leader election
                await self.get_votes()

            await asyncio.sleep(self.delay / 1000)

    # @property
    # def term(self):
    #     """
    #     get last term from logs
    #     """
    #     return self.logs[-1].term
    #
    @property
    def index(self):
        """
        get last index from logs
        """
        return self.logs[-1].index
