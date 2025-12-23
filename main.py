import argparse
import signal
from contextlib import asynccontextmanager
import os

import uvicorn
from fastapi import FastAPI, Response, status

from src.network_requests import AppendLog
from src.raft import RaftNode

node_instance: RaftNode | None = None
args = argparse.ArgumentParser()
args.add_argument("-i", "--id", type=str)
args.add_argument("-d", "--delay", type=int)
args.add_argument("-p", "--port", type=int)
args.add_argument("-lead", "--is_leader", type=bool, default=False)
parsed = vars(args.parse_args())
port = parsed["port"]


@asynccontextmanager
async def lifespan(app: FastAPI):
    global node_instance
    global parsed

    print(parsed)
    node_instance = RaftNode(**parsed)
    print(node_instance)
    await node_instance.start()

    yield

    await node_instance.stop()


app = FastAPI(lifespan=lifespan)


@app.get("/shutdown")
async def shutdown():
    os.kill(os.getpid(), signal.SIGTERM)
    return Response(status_code=200, content="Server shutting down...")


@app.post("/heartbeat")
async def heartbeat():
    assert node_instance is not None
    node_instance.receive_heartbeat()
    return {"message": "Heartbeat received"}, 200


@app.post("/appendLog")
async def append_log(log: AppendLog):
    assert node_instance is not None
    pass


@app.post("/commit")
async def commit_log(index: int):
    assert node_instance is not None
    pass


@app.get("/vote")
async def get_vote(index: int, term: int, id: str, response: Response):
    assert node_instance is not None
    print(
        f"{node_instance.id} Received vote request for term {term} and index {index} from {id}"
    )
    vote = node_instance.vote(term, index)

    response.status_code = status.HTTP_200_OK
    return {"vote": vote}


@app.get("/isLeader")
def is_leader(response: Response):
    global node_instance
    if node_instance is None:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": "Node not initialized"}

    if node_instance.is_leader:
        response.status_code = status.HTTP_200_OK
        return {"isLeader": True}
    else:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"isLeader": False}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        port=port,
    )
