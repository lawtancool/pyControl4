import aiohttp
import asyncio
import async_timeout
import json

authentication_endpoint = "https://apis.control4.com/authentication/v1/rest"
application_key = "78f6791373d61bea49fdb9fb8897f1f3af193f11"


async def getBearerToken(username, password):
    data = await sendAuthRequest(username, password)
    jsonDictionary = json.loads(data)
    return jsonDictionary["authToken"]["token"]


async def sendAuthRequest(username, password):
    dataDictionary = {
        "clientInfo": {
            "device": {
                "deviceName": "pyControl4",
                "deviceUUID": "0000000000000000",
                "make": "pyControl4",
                "model": "pyControl4",
                "os": "Android",
                "osVersion": "10",
            },
            "userInfo": {
                "applicationKey": application_key,
                "password": password,
                "userName": username,
            },
        }
    }
    async with aiohttp.ClientSession() as session:
        with async_timeout.timeout(10):
            async with session.post(
                authentication_endpoint, json=dataDictionary
            ) as resp:
                return await resp.text()
