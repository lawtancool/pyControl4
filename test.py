import pyControl4.auth
from pyControl4.director import C4Director
from pyControl4.light import C4Light
from login_info import *
import asyncio

ip = "192.168.1.25"

bearer_token = asyncio.run(pyControl4.auth.getBearerToken(username, password))

director = C4Director(ip, bearer_token)
print(asyncio.run(director.getAllItemInfo()))
# light = C4Light(director, 253)
# asyncio.run(light.rampToLevel(10, 10000))
# print(asyncio.run(light.getState()))
