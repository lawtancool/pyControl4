import aiohttp
import asyncio
import async_timeout
from .director import C4Director


class C4Light:
    def __init__(self, C4Director, item_id):
        self.director = C4Director
        self.item_id = item_id

    async def getLevel(self):
        return await self.director.getItemVariableValue(self.item_id, "LIGHT_LEVEL")

    async def setLevel(self, level):
        await self.director.sendPostRequest(
            "/api/v1/items/{}/commands".format(self.item_id),
            "SET_LEVEL",
            {"LEVEL": level},
        )

    async def rampToLevel(self, level, time):
        await self.director.sendPostRequest(
            "/api/v1/items/{}/commands".format(self.item_id),
            "RAMP_TO_LEVEL",
            {"LEVEL": level, "TIME": time},
        )
