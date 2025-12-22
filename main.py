from typing import Union
from flask import Flask, json, jsonify, make_response, request
import argparse

from src.network_requests import AppendLog, CommitLog, HeartBeat, RequestType
from src.raft import RaftNode


app = Flask(__name__)

node_instance: RaftNode | None = None
port = 3000


def init():
    global node_instance
    global port

    args = argparse.ArgumentParser()
    args.add_argument("-i", "--id", type=str)
    args.add_argument("-d", "--delay", type=int)
    args.add_argument("-p", "--port", type=int)
    parsed = vars(args.parse_args())

    # print(parsed)
    port = parsed["port"]
    node_instance = RaftNode(**parsed)


@app.post("/listen")
async def listener():
    data: Union[HeartBeat, AppendLog, CommitLog] = request.json

    if data["type"] == RequestType.HEARTBEAT:
        pass
    elif data["type"] == RequestType.APPEND_LOG:
        pass
    elif data["type"] == RequestType.COMMIT_LOG:
        pass
    else:
        return jsonify({"message": "Bad Request"}), 400

    resp = make_response()
    resp.status_code = 200
    return resp


@app.get("/isLeader")
def is_leader():
    global node_instance
    if node_instance is None:
        return jsonify({"message": "Node not initialized"}), 500

    if node_instance.is_leader:
        return jsonify({"isLeader": True}), 200
    else:
        return jsonify({"isLeader": False}), 400


if __name__ == "__main__":
    print(node_instance)
    init()
    print(node_instance)
    app.run(port=port)
