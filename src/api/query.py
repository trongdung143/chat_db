from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel
import os
from langgraph.types import Command
import json
from langchain_core.messages import HumanMessage, AIMessageChunk
import asyncio

from src.core.workflow import Workflow
from src.dependencies import get_workflow

clients = {}


class SQLRequest(BaseModel):
    sql: str


class ClientID(BaseModel):
    client_id: str


router = APIRouter()

BASE_DIR = os.path.dirname(__file__)
STATIC_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "static"))


@router.get("/", response_class=HTMLResponse)
async def get_chat_page():
    html_path = os.path.join(STATIC_DIR, "query.html")
    if not os.path.exists(html_path):
        return HTMLResponse("<h3>Chat page not found.</h3>", status_code=404)
    with open(html_path, "r", encoding="utf-8") as f:
        return f.read()


@router.get("/check_client")
async def check_client(client_id: str):
    exists = client_id in clients
    return {"exists": exists, "client_id": client_id}


@router.post("/register_client")
async def register_client(client: ClientID):
    if not client.client_id or client.client_id.strip() == "":
        return {"success": False, "message": "Client ID không được để trống"}

    if client.client_id in clients:
        return {"success": False, "message": "Client ID đã tồn tại"}

    clients[client.client_id] = True
    return {
        "success": True,
        "message": "Đăng ký thành công",
        "client_id": client.client_id,
    }


@router.get("/clear_client")
async def clear_client(
    client_id: str,
    workflow: Workflow = Depends(get_workflow),
):
    """Clear/remove a client from the server"""
    graph = workflow.get_workflow()
    graph.set
    if client_id in clients:
        del clients[client_id]
        return {"success": True, "message": "Client đã xóa"}
    return {"success": False, "message": "Client không tồn tại"}


@router.get("/query")
async def query(
    message: str,
    client_id: str,
    workflow: Workflow = Depends(get_workflow),
):
    async def generate():
        graph = workflow.get_workflow()
        input_state = {
            "question": message,
            "messages": HumanMessage(content=message),
            "answer": "",
            "next_node": "",
            "sql": "",
            "sql_error_msg": "",
            "sql_fix_count": 0,
        }

        config = {
            "configurable": {
                "thread_id": client_id,
            }
        }
        interrupt = graph.get_state(config=config).interrupts
        if interrupt:
            input_state = Command(resume=message)
        async for event in graph.astream(
            input=input_state,
            config=config,
            stream_mode=["messages", "updates", "custom"],
            subgraphs=True,
        ):
            subgraph, data_type, chunk = event
            if data_type == "messages":
                response, meta = chunk
                langgraph_node = meta.get("langgraph_node")
                if langgraph_node in [
                    "data_to_answer",
                    "simple_question",
                ] and isinstance(response, AIMessageChunk):
                    for char in response.content:
                        await asyncio.sleep(0.01)
                        yield f"data: {json.dumps({'type': 'chunk', 'response': char}, ensure_ascii=False)}\n\n"
            if data_type == "updates":
                if chunk.get("__interrupt__"):
                    for interrupt in chunk["__interrupt__"]:
                        yield f"data: {json.dumps({'type': 'chunk',
                                                    'response': interrupt.value
                                                }, ensure_ascii=False)}\n\n"
            elif data_type == "custom":
                yield f"data: {json.dumps({'type': 'step', 'response': chunk.strip()}, ensure_ascii=False)}\n\n"

        yield f"data: {json.dumps({'type': 'status', 'response': "done"}, ensure_ascii=False)}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
