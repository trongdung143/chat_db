from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import os
import logging
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from src.core.workflow import Workflow
from src.services.checkpoint_service import clear_thread
from src.services.redis_service import (
    client_exists,
    create_client,
    delete_client,
    extend_client_ttl,
)

logger = logging.getLogger(__name__)


class ClientID(BaseModel):
    client_id: str


router = APIRouter(prefix="/client/v1")

BASE_DIR = os.path.dirname(__file__)
STATIC_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "static"))


@router.get("/", response_class=HTMLResponse)
async def get_chat_page():
    html_path = os.path.join(STATIC_DIR, "index.html")
    if not os.path.exists(html_path):
        return HTMLResponse("<h3>Chat page not found.</h3>", status_code=404)

    with open(html_path, "r", encoding="utf-8") as f:
        return f.read()


@router.get("/check")
async def check_client(client_id: str):
    """Check if client session exists"""
    exists = await client_exists(client_id)
    return {"exists": exists, "client_id": client_id}


@router.post("/register")
async def register_client(client: ClientID):
    """Register a new client session"""
    if not client.client_id or client.client_id.strip() == "":
        return {"success": False, "message": "Client ID không được để trống"}

    exists = await client_exists(client.client_id)

    if exists:
        return {"success": False, "message": "Client ID đã tồn tại"}

    success = await create_client(client.client_id)

    if success:
        return {
            "success": True,
            "message": "Đăng ký thành công",
            "client_id": client.client_id,
        }
    else:
        return {"success": False, "message": "Lỗi khi đăng ký client"}


@router.post("/keepalive")
async def keepalive_client(client: ClientID):
    """Extend client session TTL (keep-alive/heartbeat)"""
    exists = await client_exists(client.client_id)

    if not exists:
        return {"success": False, "message": "Client không tồn tại"}

    success = await extend_client_ttl(client.client_id)

    if success:
        return {
            "success": True,
            "message": "Session được kéo dài",
            "client_id": client.client_id,
        }
    else:
        return {"success": False, "message": "Lỗi khi kéo dài session"}


@router.get("/clear")
async def clear_client(client_id: str, request: Request):
    """Clear/remove a client from the server"""
    try:
        workflow: Workflow = request.app.state.workflow
        checkpointer: AsyncPostgresSaver = workflow.get_checkpointer()

        config = {
            "configurable": {
                "thread_id": client_id,
            }
        }

        await checkpointer.adelete_thread(config)
        await clear_thread(client_id)

        exists = await client_exists(client_id)

        if exists:
            success = await delete_client(client_id)
            if success:
                return {"success": True, "message": "Client đã xóa"}

        return {"success": True, "message": "Client đã xóa"}

    except Exception as e:
        logger.error(f"Error clearing client {client_id}: {e}")
        return {"success": False, "message": f"Lỗi: {str(e)}"}
