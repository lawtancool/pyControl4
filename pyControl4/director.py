"""Handles communication with a Control4 Director, and provides functions for getting details about items on the Director.
"""
import aiohttp
import async_timeout
import json

from .error_handling import checkResponseForError


class C4Director:
    def __init__(
        self,
        ip,
        director_bearer_token,
        session_no_verify_ssl: aiohttp.ClientSession = None,
    ):
        """Creates a Control4 Director object.

        Parameters:
            `ip` - The IP address of the Control4 Director/Controller.

            `director_bearer_token` - The bearer token used to authenticate with the Director. See `pyControl4.account.C4Account.getDirectorBearerToken` for how to get this.

            `session` - (Optional) Allows the use of an `aiohttp.ClientSession` object for all network requests. This session will not be closed by the library.
            If not provided, the library will open and close its own `ClientSession`s as needed.
        """
        self.base_url = "https://{}".format(ip)
        self.headers = {"Authorization": "Bearer {}".format(director_bearer_token)}
        self.session = session_no_verify_ssl

    async def sendGetRequest(self, uri):
        """Sends a GET request to the specified API URI.
        Returns the Director's JSON response as a string.

        Parameters:
            `uri` - The API URI to send the request to. Do not include the IP address of the Director.
        """
        if self.session is None:
            async with aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(verify_ssl=False)
            ) as session:
                with async_timeout.timeout(10):
                    async with session.get(
                        self.base_url + uri, headers=self.headers
                    ) as resp:
                        await checkResponseForError(await resp.text())
                        return await resp.text()
        else:
            with async_timeout.timeout(10):
                async with self.session.get(
                    self.base_url + uri, headers=self.headers
                ) as resp:
                    await checkResponseForError(await resp.text())
                    return await resp.text()

    async def sendPostRequest(self, uri, command, params, async_variable=True):
        """Sends a POST request to the specified API URI. Used to send commands to the Director.
        Returns the Director's JSON response as a string.

        Parameters:
            `uri` - The API URI to send the request to. Do not include the IP address of the Director.

            `command` - The Control4 command to send.

            `params` - The parameters of the command, provided as a dictionary.
        """
        dataDictionary = {
            "async": async_variable,
            "command": command,
            "tParams": params,
        }
        if self.session is None:
            async with aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(verify_ssl=False)
            ) as session:
                with async_timeout.timeout(10):
                    async with session.post(
                        self.base_url + uri, headers=self.headers, json=dataDictionary
                    ) as resp:
                        await checkResponseForError(await resp.text())
                        return await resp.text()
        else:
            with async_timeout.timeout(10):
                async with self.session.post(
                    self.base_url + uri, headers=self.headers, json=dataDictionary
                ) as resp:
                    await checkResponseForError(await resp.text())
                    return await resp.text()

    async def getAllItemInfo(self):
        """Returns a JSON list of all the items on the Director."""
        return await self.sendGetRequest("/api/v1/items")

    async def getItemInfo(self, item_id):
        """Returns a JSON list of the details of the specified item.

        Parameters:
            `item_id` - The Control4 item ID.
        """
        return await self.sendGetRequest("/api/v1/items/{}".format(item_id))

    async def getItemSetup(self, item_id):
        """Returns a JSON list of the setup info of the specified item.

        Parameters:
            `item_id` - The Control4 item ID.
        """
        return await self.sendPostRequest(
            "/api/v1/items/{}/commands".format(item_id), "GET_SETUP", "{}", False
        )

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

    async def getAllItemVariableValue(self, var_name):
        """Returns a dictionary with the values of the specified variable for all items that have it.

        Parameters:
            `var_name` - The Control4 variable name.
        """
        data = await self.sendGetRequest(
            "/api/v1/items/variables?varnames={}".format(var_name)
        )
        if data == "[]":
            raise ValueError(
                "Empty response recieved from Director! The variable {} doesn't seem to exist for any items.".format(
                    var_name
                )
            )
        jsonDictionary = json.loads(data)
        return jsonDictionary

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
