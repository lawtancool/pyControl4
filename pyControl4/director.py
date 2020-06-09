import aiohttp
import asyncio
import async_timeout


class C4Director:
    def __init__(self, ip, bearer_token):
        self.base_url = "https://{}".format(ip)
        self.headers = {"Authorization": "Bearer {}".format(bearer_token)}

    async def sendGetRequest(self, uri):
        async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(verify_ssl=False)
        ) as session:
            with async_timeout.timeout(10):
                async with session.get(uri, headers=self.headers) as resp:
                    return await resp.text()

    async def getAllItemInfo(self):
        return await self.sendGetRequest("{}/api/v1/items".format(self.base_url))

    async def getItemInfo(self, item_id):
        return await self.sendGetRequest(
            "{}/api/v1/items/{}".format(self.base_url, item_id)
        )

    async def getItemVariables(self, item_id):
        return await self.sendGetRequest(
            "{}/api/v1/items/{}/variables".format(self.base_url, item_id)
        )

    async def getItemCommands(self, item_id):
        return await self.sendGetRequest(
            "{}/api/v1/items/{}/commands".format(self.base_url, item_id)
        )

    async def getItemNetwork(self, item_id):
        return await self.sendGetRequest(
            "{}/api/v1/items/{}/network".format(self.base_url, item_id)
        )

    async def getItemBindings(self, item_id):
        return await self.sendGetRequest(
            "{}/api/v1/items/{}/bindings".format(self.base_url, item_id)
        )
