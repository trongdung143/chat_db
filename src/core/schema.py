from langchain_core.tools.base import Field
from pydantic import BaseModel


class AssistantResponse(BaseModel):
    content: str = Field(description="Câu trả lời")
    solution_plan: str = Field(description="YES hoặc NO")
