# pyControl4
![pdoc](https://github.com/lawtancool/pyControl4/workflows/pdoc/badge.svg)![PyPI Release](https://github.com/lawtancool/pyControl4/workflows/PyPI%20Release/badge.svg)

An asynchronous library to interact with Control4 systems through their built-in REST API. This is only known to work on controllers with OS 3.0 or newer. 

Auto-generated function documentation can be found at <https://lawtancool.github.io/pycontrol4>

## Usage example
```python
from pyControl4.auth import C4Account
from pyControl4.director import C4Director
from pyControl4.light import C4Light
import asyncio
import json

username = ""
password = ""

ip = "192.168.1.25"

"""Authenticate with Control4 account"""
account = C4Account(username, password)

"""Get and print controller name"""
accountControllers = asyncio.run(account.getAccountControllers())
print(accountControllers["controllerCommonName"])

"""Get bearer token to communicate with controller locally"""
director_bearer_token = asyncio.run(
    account.getDirectorBearerToken(accountControllers["controllerCommonName"])
)

"""Create new C4Director instance"""
director = C4Director(ip, director_bearer_token)

"""Print all devices on the controller"""
print(asyncio.run(director.getAllItemInfo()))

"""Create new C4Light instance"""
light = C4Light(director, 253)

"""Ramp light level to 10% over 10000ms"""
asyncio.run(light.rampToLevel(10, 10000))

"""Print state of light"""
print(asyncio.run(light.getState()))
```