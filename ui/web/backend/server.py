from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from core.telemetry.metrics import metrics

app = FastAPI()

#@app.get("/")
def index():
    with open(
        "ui/web/frontend/index.html",
        "r"
    ) as f:
        return HTMLResponse(f.read())

@app.get("/api/telemetry")
def get_telemetry():
    return metrics.snapshot()

app.mount(
    "/",
    StaticFiles(directory="ui/web/frontend", html=True),
    name="frontend"
)

