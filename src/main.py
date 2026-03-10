from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from src.api import query, client
from src.core.workflow import Workflow
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    workflow = Workflow()
    await workflow.build_workflow()
    app.state.workflow = workflow

    yield


app = FastAPI(lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://127.0.0.1:8080"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["Set-Cookie"],
)

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
