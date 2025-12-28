import asyncio
from asyncio.tasks import Task
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

    for _ in range(NODE_COUNT):
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
        p = await asyncio.create_subprocess_exec(*cmd)
        processes.append(p)
        port += 1
        id += 1
        delay += 100

    # for i in processes:
    #     assert isinstance(i, Popen)
    #     i.wait()
    return asyncio.gather(*(p.wait() for p in processes))


async def fetch_leader():
    print("check leader running")

    async def check_leader(port: int, session: aiohttp.ClientSession):
        try:
            async with session.get(f"http://localhost:{port}/isLeader") as res:
                data = await res.json()
                return {"port": port, "isLeader": data["isLeader"]}
        except Exception:
            print(f"Node at port {port} is unreachable")
            return None

    async with aiohttp.ClientSession() as session:
        while True:
            print("check leader running")
            tasks: List[Task] = []
            for i in range(START_PORT, START_PORT + NODE_COUNT):
                tasks.append(asyncio.create_task(check_leader(i, session)))

            res = await asyncio.gather(*tasks)

            filtered_res = [r for r in res if r is not None]

            if len(filtered_res) <= NODE_COUNT // 2:
                print("Majority servers are dead, glhf...")
                return

            try:
                leader = next(node for node in filtered_res if node["isLeader"])
                print(f"leader is on port {leader['port']}")
            except StopIteration:
                print("No leader found")
            await asyncio.sleep(5)


async def ensure_all_started():
    node_status = []
    async with aiohttp.ClientSession() as session:
        while True:
            for port in range(START_PORT, START_PORT + NODE_COUNT):
                try:
                    async with session.get(f"http://localhost:{port}/health") as res:
                        data = await res.json()
                        node_status.append(True)
                        print(f"Node at port {port} is healthy")
                except Exception:
                    node_status.append(False)
                    print(f"Node at port {port} is unhealthy")
            if all(node_status):
                return True
            node_status.clear()
            await asyncio.sleep(2)


async def main():
    # node_spawner = asyncio.create_task(start_nodes())
    nodes = await start_nodes()
    await ensure_all_started()
    leader_checker = asyncio.create_task(fetch_leader())

    await asyncio.gather(
        leader_checker,
        # nodes,
    )
    await nodes


if __name__ == "__main__":
    asyncio.run(main())
