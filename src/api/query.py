from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from langgraph.types import Command
import json
from langchain_core.messages import HumanMessage, AIMessageChunk
import asyncio
from langgraph.graph.state import CompiledStateGraph


class SQLRequest(BaseModel):
    sql: str


router = APIRouter()


@router.get("/query/v1")
async def query(message: str, client_id: str, request: Request):
    async def generate():
        if not message.strip():
            yield f"data: {json.dumps({'type': 'step', 'response': "ERROR:Nhập câu hỏi!"}, ensure_ascii=False)}\n\n"
            return
        graph: CompiledStateGraph = request.app.state.workflow.get_graph()
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

        state = await graph.aget_state(config=config)
        interrupt = state.interrupts

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
