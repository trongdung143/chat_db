import asyncio
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from src.setup import DB_CHECKPOINT


async def main():
    saver_cm = AsyncPostgresSaver.from_conn_string(DB_CHECKPOINT)
    saver = await saver_cm.__aenter__()
    await saver.setup()


if __name__ == "__main__":
    asyncio.run(main())
