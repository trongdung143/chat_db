import psycopg
from src.setup import DB_CHECKPOINT

conn = None


async def get_conn():
    global conn
    if conn is None:
        conn = await psycopg.AsyncConnection.connect(DB_CHECKPOINT)
    return conn


async def clear_thread(thread_id: str):
    tables = (
        "checkpoint_writes",
        "checkpoints",
        "checkpoint_blobs",
    )

    conn = await get_conn()

    async with conn.cursor() as cur:
        for table in tables:
            await cur.execute(f"DELETE FROM {table} WHERE thread_id = %s", (thread_id,))

    await conn.commit()
