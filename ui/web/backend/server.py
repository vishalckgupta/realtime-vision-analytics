from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

#@app.get("/")
def index():
    with open(
        "ui/web/frontend/index.html",
        "r"
    ) as f:
        return HTMLResponse(f.read())

app.mount(
    "/",
    StaticFiles(directory="ui/web/frontend", html=True),
    name="frontend"
)

