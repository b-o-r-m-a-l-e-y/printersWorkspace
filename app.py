from re import L
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from printersRequester import PrintersWrapper
from configReader import ConfigReader
import asyncio


c = ConfigReader()
pw = PrintersWrapper(c.getConfig())

app = FastAPI()
app.mount("/assets", StaticFiles(directory="assets"), name="assets")

templates = Jinja2Templates(directory="templates")

printersInfo = [
    {
        'ip': '192.168.1.104',
        'octoConnected': True,
        'printerState': 'printing',
        'telemetry': {
            'bed': 24.0,
            'hotend': 25.1,
            'uptime': 2200
        }
    },
    {
        'ip': '192.168.1.100',
        'octoConnected': True,
        'printerState': 'operational'
    },
    {
        'ip': '192.168.1.99',
        'octoConnected': False,
        'printerState': 'operational'
    }
]

@app.on_event("startup")
async def startup_event():
    loop = asyncio.get_event_loop()
    loop.create_task(pw.requestTask())

@app.on_event("shutdown")
async def shutdown_event():
    pass

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, 'printersInfo': printersInfo})