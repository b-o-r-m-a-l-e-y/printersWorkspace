from fastapi import FastAPI, Request, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from printersRequester import PrintersWrapper
from configReader import ConfigReader
import asyncio
import aiohttp

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

@app.post("/upload/{id}")
async def uploadToPrinter(id: int, file: UploadFile):
    print(id)
    content = await file.read()
    data = {'file': content, 'filename': file.filename, 'path': 'RySo'}
    header={'X-Api-Key': pw.getPrintersInfo()[id].apiKey}
    async with aiohttp.ClientSession() as session:
        async with session.post(f"http://{pw.getPrintersInfo()[id].ip}/api/files/local", headers=header, data=data) as r:
            return await r.json()
