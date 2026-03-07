from langchain.agents import AgentState


class State(AgentState):
    question: str = ""
    question_detail: str = ""
    sql: str = ""
    sql_error_msg: str = ""
    list_data: list[str] = []
    answer: str = ""
    next_node: str = ""
    sql_fix_count: int = 0
