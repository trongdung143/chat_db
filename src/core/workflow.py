from langgraph.graph import StateGraph
from langchain_core.messages import AIMessage
from langgraph.config import get_stream_writer
from langsmith import traceable
from langgraph.types import interrupt
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.prebuilt.tool_node import ToolNode, tools_condition

from src.core.model import (
    sql_model,
    assistant_model,
    sql_fix_model,
)
from src.core.state import State
from src.core.prompt import (
    sql_prompt,
    assistant_prompt,
    assistant_no_data_prompt,
    sql_fix_prompt,
)
from src.database.schema_db import FULL_SCHEMA
from src.services.sql_service import SQLService
from src.database.conn_db import Database
from src.core.utils import dataframe_to_json, sanitize_sql
from src.core.tool import tools
from src.setup import DB_CHECKPOINT


class Workflow:
    def __init__(self):
        self._db = Database()
        self._sql_service = SQLService(self._db)
        self._checkpointer = None
        self._nodes = [
            "question_to_sql",
            "sql_to_data",
            "data_to_answer",
            "simple_question",
            "question_detail",
            "sql_fix",
            "__end__",
        ]
        self._graph = None
        self._tools_01 = ToolNode(tools)
        self._tools_02 = ToolNode(tools)

    def _route(self, state: State) -> str:
        next_node = state.get("next_node")

        if next_node in self._nodes:
            return state.get("next_node")

        return "__end__"

    @traceable
    async def _question_to_sql(self, state: State) -> State:
        stream_writer = get_stream_writer()
        stream_writer("INFO:Đang tạo truy vấn ...")

        try:
            chain = sql_prompt | sql_model
            response = await chain.ainvoke(
                {
                    "tables_description": FULL_SCHEMA,
                    "messages": state.get("messages"),
                }
            )

            if response.content.strip() == "SIMPLE_QUESTION":
                next_node = "simple_question"
            elif response.content.strip() == "NEED_MORE_INFO":
                next_node = "question_detail"
            else:
                next_node = "sql_to_data"

            state.update(sql=response.content, next_node=next_node)
        except Exception as e:
            stream_writer("ERROR:Lỗi khi tạo câu truy vấn!")
        return state

    def question_detail(self, state: State) -> State:
        detail = interrupt("Cần cung cấp thêm thông tin về câu hỏi!")

        question = state.get("question")
        messages = state.get("messages")

        new_question = "Câu hỏi: " + question + "\nBổ sung câu hỏi: " + detail
        messages[-1].content = new_question

        state.update(question=new_question, messages=messages)
        return state

    async def _sql_to_data(self, state: State) -> State:
        stream_writer = get_stream_writer()
        stream_writer("INFO:Đang lấy dữ liệu ...")
        try:
            sql = state.get("sql")
            sql = sanitize_sql(sql)
            df = await self._sql_service.execute(sql)
            data = dataframe_to_json(df)
            list_data = state.get("list_data", [])
            list_data.append((state.get("question"), data))
            state.update(list_data=list_data, next_node="data_to_answer")
        except Exception as e:
            stream_writer("ERROR:Lỗi khi lấy dữ liệu!")
            if state.get("sql_fix_count") >= 3:
                state.update(next_node="__end__")
                stream_writer("ERROR:Không thể lấy được dữ liệu!")
            else:
                state.update(next_node="sql_fix", sql_error_msg=str(e))

        return state

    async def _sql_fix(self, state: State) -> State:
        stream_writer = get_stream_writer()
        stream_writer("INFO:Đang sửa câu truy vấn ...")
        state.update(sql_fix_count=state.get("sql_fix_count") + 1)
        try:
            chain = sql_fix_prompt | sql_fix_model
            response = await chain.ainvoke(
                {
                    "sql": state.get("sql"),
                    "sql_error_msg": state.get("sql_error_msg"),
                    "tables_description": FULL_SCHEMA,
                }
            )
            sql = sanitize_sql(response.content)
            state.update(sql=sql, next_node="sql_to_data")
        except Exception as e:
            stream_writer("ERROR:Lỗi khi sửa câu truy vấn!")

        return state

    async def _data_to_answer(self, state: State) -> State:
        stream_writer = get_stream_writer()
        stream_writer("INFO:Đang tạo câu trả lời ...")
        try:

            chain = assistant_prompt | assistant_model.bind_tools(tools)
            response = await chain.ainvoke(
                {
                    "data_provided": state.get("list_data")[-1][1],
                    "question": state.get("question"),
                    "messages": state.get("messages"),
                }
            )
            # solution_plan = getattr(response, "solution_plan", "NO")
            # content = getattr(response, "content", " ")
            # if solution_plan == "YES":
            #     next_node = "solution_plan"
            # else:
            #     next_node = "__end__"

            state.update(
                answer=response.content,
                messages=[response],
                next_node="__end__",
            )
        except Exception as e:
            stream_writer("ERROR:Lỗi khi tạo câu trả lời ...")

        return state

    async def _simple_question(self, state: State) -> State:
        stream_writer = get_stream_writer()
        stream_writer("INFO:Đang tạo câu trả lời ...")
        try:

            chain = assistant_no_data_prompt | assistant_model.bind_tools(tools)
            response = await chain.ainvoke(
                {
                    "messages": state.get("messages"),
                }
            )

            state.update(
                answer=response.content,
                messages=[response],
                next_node="__end__",
            )
        except Exception as e:
            stream_writer("ERROR:Lỗi khi tạo câu trả lời ...")

        return state

    async def _solution_plan(self, state: State) -> State:
        stream_writer = get_stream_writer()
        stream_writer("INFO:Đang đề xuất hướng giải quyết ...")
        try:
            pass
            # chain = solution_plan_prompt | solution_plan_model
            # response = await chain.ainvoke(
            #     {
            #         "messages": state.get("messages"),
            #     }
            # )
            # state.update(
            #     answer=response.content,
            #     messages=[AIMessage(content=response.content)],
            # )
        except Exception as e:
            stream_writer("ERROR:Lỗi khi đề xuất hướng giải quyết!")

        return state

    def _build_graph(self):
        graph = StateGraph(State)

        graph.add_node("question_to_sql", self._question_to_sql)
        graph.add_node("sql_to_data", self._sql_to_data)
        graph.add_node("data_to_answer", self._data_to_answer)
        graph.add_node("simple_question", self._simple_question)
        graph.add_node("question_detail", self.question_detail)
        graph.add_node("sql_fix", self._sql_fix)
        graph.add_node("tools_01", self._tools_01)
        graph.add_node("tools_02", self._tools_02)
        # graph.add_node("solution_plan", self._solution_plan)
        graph.set_entry_point("question_to_sql")
        graph.add_conditional_edges(
            "question_to_sql",
            self._route,
            {
                "sql_to_data": "sql_to_data",
                "simple_question": "simple_question",
                "question_detail": "question_detail",
            },
        )
        graph.add_conditional_edges(
            "sql_to_data",
            self._route,
            {
                "sql_fix": "sql_fix",
                "data_to_answer": "data_to_answer",
                "__end__": "__end__",
            },
        )
        graph.add_edge("sql_fix", "sql_to_data")
        graph.add_edge("question_detail", "question_to_sql")
        graph.add_conditional_edges(
            "simple_question",
            tools_condition,
            {
                "__end__": "__end__",
                "tools": "tools_01",
            },  # , "solution_plan": "solution_plan"},
        )
        graph.add_edge("tools_01", "simple_question")
        # graph.add_edge("data_to_answer", "__end__")
        graph.add_conditional_edges(
            "data_to_answer",
            tools_condition,
            {
                "__end__": "__end__",
                "tools": "tools_02",
            },  # , "solution_plan": "solution_plan"},
        )
        graph.add_edge("tools_02", "data_to_answer")
        # graph.add_edge("solution_plan", "__end__")
        return graph.compile(checkpointer=self._checkpointer)

    def get_graph(self):
        return self._graph

    def get_checkpointer(self):
        if self._checkpointer:
            return self._checkpointer

    async def build_workflow(self):
        self._checkpointer_cm = AsyncPostgresSaver.from_conn_string(DB_CHECKPOINT)
        self._checkpointer = await self._checkpointer_cm.__aenter__()
        await self._checkpointer.setup()
        self._graph = self._build_graph()
