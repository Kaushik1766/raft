import json
import uvicorn
from typing import Union
from fastapi import FastAPI, Request, Response
from contextlib import asynccontextmanager
import argparse

from src.network_requests import AppendLog, CommitLog, GetVote, HeartBeat, RequestType
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

    # args = argparse.ArgumentParser()
    # args.add_argument("-i", "--id", type=str)
    # args.add_argument("-d", "--delay", type=int)
    # args.add_argument("-p", "--port", type=int)
    # args.add_argument("-lead", "--is_leader", type=bool, default=False)
    # parsed = vars(args.parse_args())

    print(parsed)
    node_instance = RaftNode(**parsed)
    print(node_instance)
    await node_instance.start()

    yield

    await node_instance.stop()


app = FastAPI(lifespan=lifespan)


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
async def get_vote(index: int, term: int):
    assert node_instance is not None
    vote = node_instance.vote(term, index)

    return {"vote": vote}, 200


@app.get("/isLeader")
def is_leader():
    global node_instance
    if node_instance is None:
        return {"message": "Node not initialized"}, 500

    if node_instance.is_leader:
        return {"isLeader": True}, 200
    else:
        return {"isLeader": False}, 400


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        port=port,
    )
