import asyncio
import uvicorn

if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    uvicorn.run("src.main:app", host="0.0.0.0", port=8080, reload=True)
