from sys import flags
from typing import Dict, List
import aiohttp
import asyncio
from dataclasses import dataclass
from configReader import ConfigReader
from pprint import pprint
import threading
import time

@dataclass
class PrinterTelemetry:
    bed: float = 0.0
    hotend: float = 0.0

@dataclass
class PrinterInfo:
    id: int
    ip: str
    apiKey: str
    printerState: str
    telemetry: PrinterTelemetry
    octoConnected: bool = False

class PrintersWrapper:
    def __init__(self, config):
        self.printersInfo = []
        for printerFromConfig in config:
            self.printersInfo.append(PrinterInfo(id=printerFromConfig['id'],
                                                ip=printerFromConfig['ip'],
                                                apiKey=printerFromConfig['apiKey'],
                                                printerState='closed',
                                                telemetry=PrinterTelemetry(),
                                                octoConnected=False))

    def getPrintersInfo(self):
        dictArray = []
        for printer in self.printersInfo:
            dictArray.append(printer)
        return dictArray

    async def getApiConnection(self, session: aiohttp.ClientSession, printerInfo: PrinterInfo):
        url = f"http://{printerInfo.ip}/api/connection?apikey={printerInfo.apiKey}"
        try:
            async with session.get(url) as resp:
                data = await resp.json()
                printerInfo.printerState = data['current']['state'].lower()
                printerInfo.octoConnected = True
                return data
        except aiohttp.ClientConnectionError:
            printerInfo.octoConnected = False
            print(f'No connection to printer with ip {printerInfo.ip}')

    async def getApiPrinter(self, session: aiohttp.ClientSession, printerInfo: PrinterInfo):
        url = f"http://{printerInfo.ip}/api/printer?apikey={printerInfo.apiKey}"
        try:
            async with session.get(url) as resp:
                data = await resp.json()
                try:
                    if 'flags' in data['state']:
                        flags = data['state']['flags']
                        if flags['operational']:
                            printerInfo.printerState = 'operational'
                        elif flags['printing']:
                            printerInfo.printerState = 'printing'
                        else:
                            printerInfo.printerState = 'other'
                    if 'bed' in data['temperature']:
                        printerInfo.telemetry.bed = data['temperature']['bed']['actual']
                    if 'tool0' in data['temperature']:
                        printerInfo.telemetry.hotend = data['temperature']['tool0']['actual']
                except KeyError as e:
                    print("keyerror catched", e)
                return data
        except aiohttp.ClientConnectionError:
            printerInfo.octoConnected = False
            print(f'No connection to printer with ip {printerInfo.ip}')

    async def fetchAllPrinters(self):
        session_timeout = aiohttp.ClientTimeout(total=None,sock_connect=2,sock_read=2)
        async with aiohttp.ClientSession(timeout=session_timeout) as session:
            tasks = []
            for printer in self.printersInfo:
                tasks.append(asyncio.ensure_future(self.getApiConnection(session, printer)))
                if printer.printerState != 'closed':
                    tasks.append(asyncio.ensure_future(self.getApiPrinter(session, printer)))
            await asyncio.gather(*tasks)

    async def requestTask(self):
        while(1):
            await self.fetchAllPrinters()
            await asyncio.sleep(1.0)

if __name__ == '__main__':
    c = ConfigReader()
    pw = PrintersWrapper(c.getConfig())
    asyncio.run(pw.fetchAllPrinters())
