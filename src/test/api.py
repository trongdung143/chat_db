from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import os

app = FastAPI()


BASE_DIR = os.path.dirname(__file__)
STATIC_DIR = os.path.abspath(os.path.join(BASE_DIR, "src", "static"))


@app.get("/", response_class=HTMLResponse)
async def get_chat_page():
    html_path = os.path.join(STATIC_DIR, "index.html")
    if not os.path.exists(html_path):
        return HTMLResponse("<h3>Chat page not found.</h3>", status_code=404)

    with open(html_path, "r", encoding="utf-8") as f:
        return f.read()
