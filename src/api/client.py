from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import os
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from src.core.workflow import Workflow
from src.services.checkpoint_service import clear_thread


class ClientID(BaseModel):
    client_id: str


router = APIRouter(prefix="/client/v1")

BASE_DIR = os.path.dirname(__file__)
STATIC_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "static"))


@router.get("/", response_class=HTMLResponse)
async def get_chat_page():
    html_path = os.path.join(STATIC_DIR, "query.html")
    if not os.path.exists(html_path):
        return HTMLResponse("<h3>Chat page not found.</h3>", status_code=404)
    with open(html_path, "r", encoding="utf-8") as f:
        return f.read()


@router.get("/check")
async def check_client(client_id: str, request: Request):
    clients = request.app.state.clients
    exists = client_id in clients
    return {"exists": exists, "client_id": client_id}


@router.post("/register")
async def register_client(client: ClientID, request: Request):
    clients = request.app.state.clients
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


@router.get("/clear")
async def clear_client(client_id: str, request: Request):
    """Clear/remove a client from the server"""
    clients = request.app.state.clients
    workflow: Workflow = request.app.state.workflow
    checkpointer: AsyncPostgresSaver = workflow.get_checkpointer()
    config = {
        "configurable": {
            "thread_id": client_id,
        }
    }
    await checkpointer.adelete_thread(config)
    await clear_thread(client_id)
    if client_id in clients:
        del clients[client_id]
        return {"success": True, "message": "Client đã xóa"}
    return {"success": False, "message": "Client không tồn tại"}
