import os
import sys
import json
import asyncio
import argparse

from pyControl4.account import C4Account
from pyControl4.director import C4Director


async def list_devices(username, password, ip, category=None, limit=None):
    account = C4Account(username, password)
    await account.getAccountBearerToken()
    acct = await account.getAccountControllers()
    token_info = await account.getDirectorBearerToken(acct["controllerCommonName"])
    director = C4Director(ip, token_info["token"])

    if category:
        data = await director.getAllItemsByCategory(category)
    else:
        data = await director.getAllItemInfo()

    items = json.loads(data)
    if not isinstance(items, list):
        print("Unexpected response format:")
        print(items)
        return 1

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
        print(f"- name={name} id={item_id} category={category_name} room={room} model={model} manufacturer={manufacturer} control={control} protocolControl={protocolControl} ")
        #print(it)
    return 0


def main(argv):
    parser = argparse.ArgumentParser(description="List Control4 devices from Director")
    parser.add_argument("--username", default=os.getenv("C4_USERNAME"), help="Control4 username (env C4_USERNAME)")
    parser.add_argument("--password", default=os.getenv("C4_PASSWORD"), help="Control4 password (env C4_PASSWORD)")
    parser.add_argument("--ip", default=os.getenv("C4_DIRECTOR_IP"), help="Director IP (env C4_DIRECTOR_IP)")
    parser.add_argument("--category", default=None, help="Optional category filter (e.g. lights)")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of printed items")

    args = parser.parse_args(argv)
    missing = [k for k, v in {"username": args.username, "password": args.password, "ip": args.ip}.items() if not v]
    if missing:
        print(f"Missing required args or env: {', '.join(missing)}")
        parser.print_help()
        return 2

    try:
        return asyncio.run(list_devices(args.username, args.password, args.ip, args.category, args.limit))
    except Exception as exc:
        print(f"Error: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))


