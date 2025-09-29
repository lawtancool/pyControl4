from pyControl4.account import C4Account
from pyControl4.director import C4Director
from pyControl4.error_handling import checkResponseForError

import asyncio
import json
import aiohttp
import argparse
import os
import sys


def _parse_properties(path):
    creds = {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                s = line.strip()
                if not s or s.startswith("#") or s.startswith(";"):
                    continue
                if "=" in s:
                    k, v = s.split("=", 1)
                elif ":" in s:
                    k, v = s.split(":", 1)
                else:
                    continue
                creds[k.strip()] = v.strip().strip('"').strip("'")
    except FileNotFoundError:
        return None
    return creds


def _load_credentials():
    base_dir = os.path.dirname(__file__)
    candidates = [
        os.path.join(base_dir, "c4.properties"),
    ]
    for path in candidates:
        if not os.path.isfile(path):
            continue
        data = _parse_properties(path)
        if data:
            return {
                "ip": data.get("ip"),
                "username": data.get("username"),
                "password": data.get("password"),
            }
    return None


parser = argparse.ArgumentParser(
    description="Run Control4 test script against a Director",
)
parser.add_argument("--ip", help="Director IP address")
parser.add_argument("--username", help="Control4 account username/email")
parser.add_argument("--password", help="Control4 account password")
parser.add_argument(
    "--list-all",
    action="store_true",
    help="Query and pretty print all available devices",
)
parser.add_argument("--limit", type=int, help="Limit number of listed items")
args = parser.parse_args()

_cfg = _load_credentials()
ip = args.ip or (_cfg and _cfg.get("ip"))
username = args.username or (_cfg and _cfg.get("username"))
password = args.password or (_cfg and _cfg.get("password"))

if not ip or not username or not password:
    print(
        "Missing credentials. Provide via c4.properties (ip, username, password) or CLI --ip --username --password.",
        file=sys.stderr,
    )
    parser.print_help()
    sys.exit(2)


async def returnClientSession():
    session = aiohttp.ClientSession()
    return session


def print_all_devices(director: C4Director, limit: int | None = None):
    items_json = asyncio.run(director.getAllItemInfo())
    try:
        items = json.loads(items_json)
    except Exception:
        print("Unexpected response format:")
        print(items_json)
        return
    if not isinstance(items, list):
        print("Unexpected response format:")
        print(items)
        return
    print(f"Total items: {len(items)}")
    if limit is not None:
        items = items[:limit]
    for it in items:
        name = it.get("name")
        item_id = it.get("id")
        category_name = it.get("category")
        room = it.get("room")
        model = it.get("model")
        control = it.get("control")
        manufacturer = it.get("manufacturer")
        protocolControl = it.get("protocolControl")
        print(
            f"- name={name} id={item_id} category={category_name} room={room} model={model} manufacturer={manufacturer} control={control} protocolControl={protocolControl} "
        )


# Authenticate and connect
account = C4Account(username, password)
asyncio.run(account.getAccountBearerToken())
acct = asyncio.run(account.getAccountControllers())
director_bearer_token = asyncio.run(
    account.getDirectorBearerToken(acct["controllerCommonName"])
)
director = C4Director(ip, director_bearer_token["token"])

if args.list_all:
    print_all_devices(director, args.limit)
    sys.exit(0)

print("Connected to Director.")

# ---------------------------------------------------------------------------
# Examples (kept for reference):
#
# Uncomment any of the lines below to try specific operations.
# ---------------------------------------------------------------------------

# Sanity-check error handling with a known error payload
# asyncio.run(
#     checkResponseForError(
#         '{"code":404,"details":"Account with id:527154 not found in DB","message":"Account not found","subCode":0}'
#     )
# )

# Manually create a reusable aiohttp session
# async def returnClientSession():
#     session = aiohttp.ClientSession()
#     return session
# session = asyncio.run(returnClientSession())

# Account/controller info
# print(asyncio.run(account.getAccountControllers()))
# print(acct["controllerCommonName"])
# print(acct["href"])
# print(asyncio.run(account.getControllerOSVersion(acct["href"])))

# Director bearer token
# print(director_bearer_token)

# Alarm usage examples
# from pyControl4.alarm import C4SecurityPanel, C4ContactSensor
# alarm = C4SecurityPanel(director, 460)
# print(asyncio.run(alarm.getEmergencyTypes()))
# print(asyncio.run(director.getItemSetup(471)))
# sensor = C4ContactSensor(director, 471)
# print(asyncio.run(sensor.getContactState()))

# Dump all items to a file
# with open("allitems.txt", "w", encoding="utf-8") as f:
#     f.write(asyncio.run(director.getAllItemInfo()))

# Query a variable across all items
# print(asyncio.run(director.getAllItemVariableValue("LIGHT_LEVEL")))

# Light control example
# from pyControl4.light import C4Light
# light = C4Light(director, 253)
# asyncio.run(light.rampToLevel(10, 10000))
# print(asyncio.run(light.getState()))
