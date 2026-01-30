from pyControl4.account import C4Account
from pyControl4.director import C4Director
from pyControl4.light import C4Light
from pyControl4.alarm import C4SecurityPanel, C4ContactSensor
from pyControl4.error_handling import checkResponseForError

from login_info import *
import asyncio
import json
import aiohttp

ip = "192.168.1.25"

# asyncio.run(
#     checkResponseForError(
#         '{"code":404,"details":"Account with id:527154 not found in DB","message":"Account not found","subCode":0}'
#     )
# )


async def returnClientSession():
    session = aiohttp.ClientSession()
    return session


# session = asyncio.run(returnClientSession())

account = C4Account(username, password)
asyncio.run(account.getAccountBearerToken())
data = asyncio.run(account.getAccountControllers())
# print(asyncio.run(account.getAccountControllers()))
# print(data["controllerCommonName"])
# print(data["href"])
# print(asyncio.run(account.getControllerOSVersion(data["href"])))

director_bearer_token = asyncio.run(
    account.getDirectorBearerToken(data["controllerCommonName"])
)
# print(director_bearer_token)
director = C4Director(ip, director_bearer_token["token"])

alarm = C4SecurityPanel(director, 460)
print(asyncio.run(alarm.getEmergencyTypes()))

print(asyncio.run(director.getItemSetup(471)))

# sensor = C4ContactSensor(director, 471)
# print(asyncio.run(sensor.getContactState()))

# f = open("allitems.txt", "x")

# f.write(asyncio.run(director.getAllItemInfo()))
# f.close()

# print(asyncio.run(director.getAllItemVariableValue("LIGHT_LEVEL")))

# light = C4Light(director, 253)
# asyncio.run(light.rampToLevel(10, 10000))
# print(asyncio.run(light.getState()))
