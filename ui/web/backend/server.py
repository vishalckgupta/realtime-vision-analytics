from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/")
def index():
    with open(
        "ui/web/frontend/index.html",
        "r"
    ) as f:
        return HTMLResponse(f.read())

