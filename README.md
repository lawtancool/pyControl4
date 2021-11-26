# pyControl4
[![PyPI version](https://badge.fury.io/py/pyControl4.svg)](https://badge.fury.io/py/pyControl4)[![Downloads](https://pepy.tech/badge/pycontrol4)](https://pepy.tech/project/pycontrol4)

[![CI](https://github.com/lawtancool/pyControl4/workflows/CI/badge.svg)](https://github.com/lawtancool/pyControl4/actions?query=workflow%3ACI)[![pdoc](https://github.com/lawtancool/pyControl4/workflows/pdoc/badge.svg)](https://github.com/lawtancool/pyControl4/actions?query=workflow%3Apdoc)[![PyPI Release](https://github.com/lawtancool/pyControl4/workflows/PyPI%20Release/badge.svg)](https://github.com/lawtancool/pyControl4/actions?query=workflow%3A%22PyPI+Release%22)


An asynchronous library to interact with Control4 systems through their built-in REST API. This is known to work on controllers with OS 2.10.1.544795-res and OS 3.0+. 

Auto-generated function documentation can be found at <https://lawtancool.github.io/pyControl4>

For those who are looking for a pre-built solution for controlling their devices, this library is implemented in the [official Home Assistant Control4 integration](https://www.home-assistant.io/integrations/control4/).

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
asyncio.run(account.getAccountBearerToken())

"""Get and print controller name"""
accountControllers = asyncio.run(account.getAccountControllers())
print(accountControllers["controllerCommonName"])

"""Get bearer token to communicate with controller locally"""
director_bearer_token = asyncio.run(
    account.getDirectorBearerToken(accountControllers["controllerCommonName"])
)["token"]

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

## Contributing
Pull requests are welcome! Please lint your Python code with `flake8` and format it with [Black](https://pypi.org/project/black/).

## Disclaimer
This library is not affiliated with or endorsed by Control4. 
