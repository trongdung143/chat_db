from src.setup import OPENROUTER_API_KEY
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langchain.agents import AgentState
from langchain_core.messages import AIMessage
from langchain.tools import tool, ToolRuntime
from langgraph.prebuilt.tool_node import tools_condition, ToolNode
import json
from langchain_openai import ChatOpenAI
from src.core.prompt import prompt_sql
from src.schema.schema_db import (
    FULL_SCHEMA_01,
    FULL_SCHEMA_02,
    FULL_SCHEMA_02_SAMPLE_DATA,
)


class State(AgentState):
    pass


llm = ChatOpenAI(
    model="google/gemini-2.5-flash",
    temperature=0,
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
    streaming=True,
    # openrouter_provider={"order": ["Anthropic"]},
)


chain = prompt_sql | llm

# async def get_data_db(state: State) -> State:
#     """Dùng để lấy tên chính xác của tất cả sản trong database dựa theo tên người dùng nói."""
#     try:
#         cursor = connection.cursor()
#         cursor.execute(f"SELECT name FROM product")
#         columns = [desc[0] for desc in cursor.description]
#         rows = cursor.fetchall()
#         data = [dict(zip(columns, row)) for row in rows]
#         cursor.close()
#         state.update(sp=data)
#         return state
#     except Exception as e:
#         return json.dumps({"error": str(e)})


async def process(state: State) -> State:
    response = await chain.ainvoke(
        {
            "tables_description": FULL_SCHEMA_02_SAMPLE_DATA,
            "messages": state.get("messages"),
        }
    )
    state.update(messages=[AIMessage(content=response.content)])
    return state


graph = StateGraph(State)
graph.add_node("process", process)
graph.set_entry_point("process")
graph = graph.compile(checkpointer=MemorySaver())
