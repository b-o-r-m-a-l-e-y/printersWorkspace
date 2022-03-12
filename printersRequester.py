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
    ip: str
    apiKey: str
    printerState: str
    telemetry: PrinterTelemetry
    octoConnected: bool = False

class PrintersWrapper:
    def __init__(self, config):
        self.printersInfo = []
        for printerFromConfig in config:
            self.printersInfo.append(PrinterInfo(ip=printerFromConfig['ip'],
                                                apiKey=printerFromConfig['apiKey'],
                                                printerState='Closed',
                                                telemetry=PrinterTelemetry(),
                                                octoConnected=True))

    def getPrintersInfo(self):
        return self.printersInfo

    async def getApiConnection(self, session: aiohttp.ClientSession, printerInfo: PrinterInfo):
        url = f"http://{printerInfo.ip}/api/connection?apikey={printerInfo.apiKey}"
        try:
            async with session.get(url) as resp:
                data = await resp.json()
                printerInfo.printerState = data['current']['state']
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
                        if flags['printing']:
                            printerInfo.printerState = 'printing'
                        else:
                            printerInfo.printerState = 'other'
                except KeyError:
                    print("keyerror catched")
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
                if printer.octoConnected:
                    tasks.append(asyncio.ensure_future(self.getApiPrinter(session, printer)))
            await asyncio.gather(*tasks)
    
    def run(self):
        asyncio.run(self.fetchAllPrinters())

if __name__ == '__main__':
    c = ConfigReader()
    pw = PrintersWrapper(c.getConfig())
    # pw.getPrintersInfo()[0].printerState = 'new'
    # print(pw.getPrintersInfo())
    pw.run()