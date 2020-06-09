"""
To use, create a file called bearer_token.py with the contents
    bearer_token = YOUR_BEARER_TOKEN_WITHOUT_THE_WORD_BEARER_IN_FRONT
"""


from pyControl4.director import C4Director
from pyControl4.light import C4Light
from bearer_token import *
import asyncio

ip = "192.168.1.25"

director = C4Director(ip, bearer_token)
# print(asyncio.run(director.getAllItemInfo()))
light = C4Light(director, 253)
asyncio.run(light.setLevel(2))
print(asyncio.run(light.getLevel()))
