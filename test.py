import pyControl4.auth
from pyControl4.director import C4Director
from pyControl4.light import C4Light
from login_info import *
import asyncio
import json

ip = "192.168.1.25"

account_bearer_token = asyncio.run(
    pyControl4.auth.getAccountBearerToken(username, password)
)
print(account_bearer_token)
data = asyncio.run(pyControl4.auth.getAccountControllers(account_bearer_token))
print(data["controllerCommonName"])
director_bearer_token = asyncio.run(
    pyControl4.auth.getDirectorBearerToken(
        account_bearer_token, data["controllerCommonName"]
    )
)
print(director_bearer_token)
director = C4Director(ip, director_bearer_token)
print(asyncio.run(director.getAllItemInfo()))
# light = C4Light(director, 253)
# asyncio.run(light.rampToLevel(10, 10000))
# print(asyncio.run(light.getState()))
