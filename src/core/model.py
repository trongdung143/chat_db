from langchain_openai import ChatOpenAI
from src.setup import OPENROUTER_API_KEY
from src.core.schema import AssistantResponse

sql_model = ChatOpenAI(
    model="openai/gpt-oss-120b",
    temperature=0,
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
    streaming=True,
    reasoning_effort="high",
)

assistant_model = ChatOpenAI(
    model="openai/gpt-4o-mini",
    temperature=0,
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
    streaming=True,
)  # .with_structured_output(AssistantResponse)


sql_fix_model = ChatOpenAI(
    model="openai/gpt-oss-120b",
    temperature=0,
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
    streaming=True,
    reasoning_effort="high",
)


solution_plan_model = ChatOpenAI(
    model="google/gemini-2.5-flash",
    temperature=0,
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
    streaming=True,
)


business_rule_model = ChatOpenAI(
    model="openai/gpt-4o-mini",
    temperature=0,
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
    streaming=True,
)
