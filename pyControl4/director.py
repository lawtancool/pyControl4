import aiohttp
import asyncio
import async_timeout
import json


class C4Director:
    def __init__(self, ip, bearer_token):
        self.base_url = "https://{}".format(ip)
        self.headers = {"Authorization": "Bearer {}".format(bearer_token)}

    async def sendGetRequest(self, uri):
        async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(verify_ssl=False)
        ) as session:
            with async_timeout.timeout(10):
                async with session.get(
                    self.base_url + uri, headers=self.headers
                ) as resp:
                    return await resp.text()

    # params should be a dictionary with the params
    async def sendPostRequest(self, uri, command, params):
        dataDictionary = {"async": True, "command": command, "tParams": params}
        async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(verify_ssl=False)
        ) as session:
            with async_timeout.timeout(10):
                async with session.post(
                    self.base_url + uri, headers=self.headers, json=dataDictionary
                ) as resp:
                    return await resp.text()

    async def getAllItemInfo(self):
        return await self.sendGetRequest("/api/v1/items")

    async def getItemInfo(self, item_id):
        return await self.sendGetRequest("/api/v1/items/{}".format(item_id))

    async def getItemVariables(self, item_id):
        return await self.sendGetRequest("/api/v1/items/{}/variables".format(item_id))

    async def getItemVariableValue(self, item_id, var_name):
        data = await self.sendGetRequest(
            "/api/v1/items/{}/variables?varnames={}".format(item_id, var_name)
        )
        jsonDictionary = json.loads(data)
        return jsonDictionary[0]["value"]

    async def getItemCommands(self, item_id):
        return await self.sendGetRequest("/api/v1/items/{}/commands".format(item_id))

    async def getItemNetwork(self, item_id):
        return await self.sendGetRequest("/api/v1/items/{}/network".format(item_id))

    async def getItemBindings(self, item_id):
        return await self.sendGetRequest("/api/v1/items/{}/bindings".format(item_id))
