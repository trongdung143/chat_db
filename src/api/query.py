from fastapi import APIRouter
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel
import os
from src.core.chain import graph
from src.connection import engine
import json
import re
from langchain_core.messages import HumanMessage, AIMessageChunk
from fastapi import HTTPException
import asyncio
import pandas as pd


class SQLRequest(BaseModel):
    sql: str


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


@router.get("/query")
async def query(message: str):
    async def generate():
        full_response = ""
        input_state = {
            "messages": HumanMessage(content=message),
        }

        config = {
            "configurable": {
                "thread_id": "123",
            }
        }
        async for chunk in graph.astream(input_state, config, stream_mode="messages"):
            response, meta = chunk
            if isinstance(response, AIMessageChunk):
                full_response += response.content
                for c in response.content:
                    await asyncio.sleep(0.01)
                    yield f"data: {json.dumps({'type': 'chunk', 'response': c}, ensure_ascii=False)}\n\n"

        match = re.search(
            r"---SQL START---(.*?)---SQL END---", full_response, re.DOTALL
        )
        sql = match.group(1).strip() if match else ""

        yield f"data: {json.dumps({'type': 'sql', 'response': sql}, ensure_ascii=False)}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.post("/get_data")
async def get_data(request: SQLRequest):
    sql = request.sql

    try:
        (sql)

        sql_type = sql.strip().split()[0].upper()

        if sql_type == "SELECT":
            if cursor.description is None:
                return []

            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            data = [dict(zip(columns, row)) for row in rows]
            return data

        else:
            conn.commit()  #
            return [{"affected_rows": cursor.rowcount}]

    except Exception as e:
        conn.rollback()  #
        raise HTTPException(status_code=400, detail=str(e))
