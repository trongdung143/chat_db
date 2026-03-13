from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import os

from src.api import query, client
from src.core.workflow import Workflow
from src.services.redis_service import close_redis
from contextlib import asynccontextmanager
import logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    workflow = Workflow()
    await workflow.build_workflow()
    app.state.workflow = workflow
    logger.info("Application startup complete")
    yield
    # Cleanup on shutdown
    logger.info("Shutting down application...")
    await close_redis()
    logger.info("Application shutdown complete")


app = FastAPI(lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["Set-Cookie"],
)

BASE_DIR = os.path.dirname(__file__)
STATIC_DIR = os.path.abspath(os.path.join(BASE_DIR, "static"))
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
BLOCKED_KEYWORDS = ["wget", "chmod", "rm", ";", "curl", "tftp", "ftpget"]


@app.middleware("http")
async def block_malicious_requests(request: Request, call_next):
    try:
        raw_url = str(request.url)
        if any(
            keyword in raw_url.lower()
            for keyword in ["wget", "curl", "sh ", "rm ", "chmod"]
        ):
            return JSONResponse(
                status_code=403,
                content={"detail": "Blocked request due to potential security risk."},
            )
        response = await call_next(request)
        return response
    except Exception:
        return JSONResponse(
            status_code=500, content={"detail": "Internal server error."}
        )


app.include_router(query.router)
app.include_router(client.router)
