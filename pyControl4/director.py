"""Handles communication with a Control4 Director, and provides functions for getting details about items on the Director.
"""
import aiohttp
import asyncio
import async_timeout
import json


class C4Director:
    def __init__(self, ip, director_bearer_token):
        """Creates a Control4 Director object.

        Parameters:
            `ip` - The IP address of the Control4 Director/Controller.

            `director_bearer_token` - The bearer token used to authenticate with the Director. See `auth.py` for how to get this.
        """
        self.base_url = "https://{}".format(ip)
        self.headers = {"Authorization": "Bearer {}".format(director_bearer_token)}

    async def sendGetRequest(self, uri):
        """Sends a GET request to the specified API URI.
        Returns the Director's JSON response as a string.
        
        Parameters:
            `uri` - The API URI to send the request to. Do not include the IP address of the Director.
        """
        async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(verify_ssl=False)
        ) as session:
            with async_timeout.timeout(10):
                async with session.get(
                    self.base_url + uri, headers=self.headers
                ) as resp:
                    return await resp.text()

    async def sendPostRequest(self, uri, command, params):
        """Sends a POST request to the specified API URI. Used to send commands to the Director.
        Returns the Director's JSON response as a string.

        Parameters:
            `uri` - The API URI to send the request to. Do not include the IP address of the Director.

            `command` - The Control4 command to send.

            `params` - The parameters of the command, provided as a dictionary.
        """
        dataDictionary = {"async": True, "command": command, "tParams": params}
        async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(verify_ssl=False)
        ) as session:
            with async_timeout.timeout(10):
                async with session.post(
                    self.base_url + uri, headers=self.headers, json=dataDictionary
                ) as resp:
                    return await resp.text()

    async def getAllItemInfo(self):
        """Returns a JSON list of all the items on the Director.
        """
        return await self.sendGetRequest("/api/v1/items")

    async def getItemInfo(self, item_id):
        """Returns a JSON list of the details of the specified item.

        Parameters:
            `item_id` - The Control4 item ID.
        """
        return await self.sendGetRequest("/api/v1/items/{}".format(item_id))

    async def getItemVariables(self, item_id):
        """Returns a JSON list of the variables available for the specified item.

        Parameters:
            `item_id` - The Control4 item ID.
        """
        return await self.sendGetRequest("/api/v1/items/{}/variables".format(item_id))

    async def getItemVariableValue(self, item_id, var_name):
        """Returns the value of the specified variable for the specified item as a string.

        Parameters:
            `item_id` - The Control4 item ID.
            
            `var_name` - The Control4 variable name.
        """
        data = await self.sendGetRequest(
            "/api/v1/items/{}/variables?varnames={}".format(item_id, var_name)
        )
        if data == "[]":
            raise ValueError(
                "Empty response recieved from Director! The variable {} doesn't seem to exist for item {}.".format(
                    var_name, item_id
                )
            )
        jsonDictionary = json.loads(data)
        return jsonDictionary[0]["value"]

    async def getItemCommands(self, item_id):
        """Returns a JSON list of the commands available for the specified item.

        Parameters:
            `item_id` - The Control4 item ID.
        """
        return await self.sendGetRequest("/api/v1/items/{}/commands".format(item_id))

    async def getItemNetwork(self, item_id):
        """Returns a JSON list of the network information for the specified item.

        Parameters:
            `item_id` - The Control4 item ID.
        """
        return await self.sendGetRequest("/api/v1/items/{}/network".format(item_id))

    async def getItemBindings(self, item_id):
        """Returns a JSON list of the bindings information for the specified item.

        Parameters:
            `item_id` - The Control4 item ID.
        """
        return await self.sendGetRequest("/api/v1/items/{}/bindings".format(item_id))
