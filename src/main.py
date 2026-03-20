import json
import time
from collections import deque
from datetime import datetime

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(title="Webhook Inspector")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

request_log: deque = deque(maxlen=100)
active_websockets: list[WebSocket] = []


async def broadcast(data: dict):
    dead = []
    for ws in active_websockets:
        try:
            await ws.send_json(data)
        except Exception:
            dead.append(ws)
    for ws in dead:
        active_websockets.remove(ws)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_websockets.append(websocket)
    await websocket.send_json({"type": "history", "requests": list(request_log)})
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        if websocket in active_websockets:
            active_websockets.remove(websocket)


@app.api_route(
    "/hook/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"],
)
async def catch_webhook(request: Request, path: str = ""):
    body_bytes = await request.body()
    body_text = body_bytes.decode("utf-8", errors="replace")

    body_parsed = None
    try:
        body_parsed = json.loads(body_text)
    except Exception:
        pass

    entry = {
        "id": f"{int(time.time() * 1000)}",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "method": request.method,
        "path": f"/hook/{path}" if path else "/hook",
        "query": dict(request.query_params),
        "headers": dict(request.headers),
        "body_raw": body_text,
        "body_parsed": body_parsed,
        "client": request.client.host if request.client else "unknown",
    }

    request_log.appendleft(entry)
    await broadcast({"type": "new_request", "request": entry})

    return {"status": "received", "id": entry["id"]}


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
