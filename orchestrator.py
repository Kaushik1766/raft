import asyncio
from asyncio.tasks import Task
from functools import reduce
from itertools import count
from subprocess import Popen
from typing import List

import aiohttp

NODE_COUNT = 5
START_PORT = 3000
BASE_DELAY = 1000

async def start_nodes():
    processes = []
    port = START_PORT
    id = 1
    delay = BASE_DELAY

    for i in range(NODE_COUNT):
        cmd = [
            "python3",
            "main.py",
            "-i",
            str(id),
            "-d",
            str(delay),
            "-p",
            str(port),
        ]
        # p = Popen(cmd)
        p = asyncio.create_subprocess_exec(
            *cmd
        )
        processes.append(p)
        port += 1
        id += 1
        # delay += 100

    # for i in processes:
    #     assert isinstance(i, Popen)
    #     i.wait()
    await asyncio

async def fetch_leader():
    print("check leader running")
    async def check_leader(port:int, session: aiohttp.ClientSession):
        try:
            async with session.get(f"http://localhost:{port}/isLeader") as res:
                data = await res.json()
                return {
                    "port":port,
                    "isLeader":data["isLeader"]
                }
        except Exception:
            print(f"Node at port {port} is unreachable")
            return

    async with aiohttp.ClientSession() as session:
        while True:
            print("check leader running")
            tasks: List[Task] = []
            for i in range(START_PORT,START_PORT + NODE_COUNT):
                tasks.append(asyncio.create_task(check_leader(i, session)))

            res = await asyncio.gather(*tasks)

            if len(res) <= NODE_COUNT//2:
                print("Majority servers are dead, glhf...")
                return

            leader = reduce(lambda acc, x: x['port'] if ( x['isLeader']) else acc, res, 0)
            print(f"leader is on port {leader}")
            await asyncio.sleep(5)






async def main():
    node_spawner = asyncio.create_task(start_nodes())
    leader_checker = asyncio.create_task(fetch_leader())

    await asyncio.gather(node_spawner, leader_checker)



if __name__ == "__main__":
    asyncio.run(main())
