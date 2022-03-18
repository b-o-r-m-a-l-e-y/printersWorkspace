from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from printersRequester import PrintersWrapper
from configReader import ConfigReader
import asyncio

pw = PrintersWrapper(ConfigReader().getConfig())

app = FastAPI()
app.mount("/assets", StaticFiles(directory="assets"), name="assets")

templates = Jinja2Templates(directory="templates")

@app.on_event("startup")
async def startup_event():
    loop = asyncio.get_event_loop()
    loop.create_task(pw.requestTask())

#Check offline
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    print(pw.getPrintersInfo())
    return templates.TemplateResponse("index.html", {"request": request, 'printersInfo': pw.getPrintersInfo()})