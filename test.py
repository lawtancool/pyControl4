from pyControl4.auth import C4Auth
from pyControl4.director import C4Director
from pyControl4.light import C4Light
from login_info import *
import asyncio
import json

ip = "192.168.1.25"

account = C4Auth(username, password)
data = asyncio.run(account.getAccountControllers())
print(data["controllerCommonName"])
# director_bearer_token = asyncio.run(
#     account.getDirectorBearerToken(data["controllerCommonName"])
# )
# print(director_bearer_token)
# director = C4Director(ip, director_bearer_token)
# print(asyncio.run(director.getAllItemInfo()))

# light = C4Light(director, 253)
# asyncio.run(light.rampToLevel(10, 10000))
# print(asyncio.run(light.getState()))
