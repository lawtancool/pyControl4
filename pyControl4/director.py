"""Handles communication with a Control4 Director, and provides functions for
getting details about items on the Director.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

import aiohttp
import asyncio
import json

from .error_handling import check_response_for_error


class C4Director:
    def __init__(
        self,
        ip,
        director_bearer_token,
        session_no_verify_ssl: aiohttp.ClientSession | None = None,
    ):
        """Creates a Control4 Director object.

        Parameters:
            `ip` - The IP address of the Control4 Director/Controller.

            `director_bearer_token` - The bearer token used to authenticate
                                      with the Director.
                See `pyControl4.account.C4Account.getDirectorBearerToken`
                for how to get this.

            `session` - (Optional) Allows the use of an
                        `aiohttp.ClientSession` object
                        for all network requests. This
                        session will not be closed by the library.
                        If not provided, the library will open and
                        close its own `ClientSession`s as needed.
        """
        self.base_url = f"https://{ip}"
        self.headers = {"Authorization": f"Bearer {director_bearer_token}"}
        self.director_bearer_token = director_bearer_token
        self.session = session_no_verify_ssl

    @asynccontextmanager
    async def _get_session(self) -> AsyncGenerator[aiohttp.ClientSession, None]:
        """Returns the configured session or creates a temporary one.

        If self.session is set, yields it without closing.
        Otherwise, creates and closes a temporary session.
        """
        if self.session is not None:
            yield self.session
        else:
            async with aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(verify_ssl=False)
            ) as session:
                yield session

    async def send_get_request(self, uri: str) -> str:
        """Sends a GET request to the specified API URI.
        Returns the Director's JSON response as a string.

        Parameters:
            `uri` - The API URI to send the request to. Do not include the IP
                    address of the Director.
        """
        async with self._get_session() as session:
            async with asyncio.timeout(10):
                async with session.get(
                    self.base_url + uri, headers=self.headers
                ) as resp:
                    await check_response_for_error(await resp.text())
                    return await resp.text()

    async def send_post_request(
        self, uri: str, command: str, params: dict, is_async: bool = True
    ) -> str:
        """Sends a POST request to the specified API URI. Used to send commands
           to the Director.
        Returns the Director's JSON response as a string.

        Parameters:
            `uri` - The API URI to send the request to. Do not include the IP
                    address of the Director.

            `command` - The Control4 command to send.

            `params` - The parameters of the command, provided as a dictionary.
        """
        data_dict = {
            "async": is_async,
            "command": command,
            "tParams": params,
        }
        async with self._get_session() as session:
            async with asyncio.timeout(10):
                async with session.post(
                    self.base_url + uri, headers=self.headers, json=data_dict
                ) as resp:
                    await check_response_for_error(await resp.text())
                    return await resp.text()

    async def get_all_items_by_category(self, category: str) -> list[dict]:
        """Returns a list of items related to a particular category.

        Parameters:
            `category` - Control4 Category Name: controllers, comfort, lights,
                         cameras, sensors, audio_video,
                         motorization, thermostats, motors,
                         control4_remote_hub,
                         outlet_wireless_dimmer, voice-scene
        """
        data = await self.send_get_request(f"/api/v1/categories/{category}")
        return json.loads(data)

    async def get_all_item_info(self) -> list[dict]:
        """Returns a list of all the items on the Director."""
        data = await self.send_get_request("/api/v1/items")
        return json.loads(data)

    async def get_item_info(self, item_id: int) -> list[dict]:
        """Returns a list of the details of the specified item.

        Parameters:
            `item_id` - The Control4 item ID.
        """
        data = await self.send_get_request(f"/api/v1/items/{item_id}")
        return json.loads(data)

    async def get_item_setup(self, item_id: int) -> dict:
        """Returns the setup info of the specified item.

        Parameters:
            `item_id` - The Control4 item ID.
        """
        data = await self.send_post_request(
            f"/api/v1/items/{item_id}/commands", "GET_SETUP", {}, False
        )
        return json.loads(data)

    async def get_item_variables(self, item_id: int) -> list[dict]:
        """Returns a list of the variables available for the specified item.

        Parameters:
            `item_id` - The Control4 item ID.
        """
        data = await self.send_get_request(f"/api/v1/items/{item_id}/variables")
        return json.loads(data)

    async def get_item_variable_value(
        self, item_id: int, var_name: str | list | tuple | set
    ) -> Any | None:
        """Returns the value of the specified variable for the
        specified item.

        The returned value is the JSON ``"value"`` field from the Director
        response. If that field is the string ``"Undefined"``, this method
        returns ``None``.
        Parameters:
            `item_id` - The Control4 item ID.

            `var_name` - The Control4 variable name or names.
        """

        if isinstance(var_name, (tuple, list, set)):
            var_name = ",".join(var_name)

        data = await self.send_get_request(
            f"/api/v1/items/{item_id}/variables?varnames={var_name}"
        )
        if data == "[]":
            raise ValueError(
                f"Empty response received from Director! The variable {var_name} "
                f"doesn't seem to exist for item {item_id}."
            )
        json_dict = json.loads(data)
        if not json_dict or not isinstance(json_dict, list) or len(json_dict) == 0:
            raise ValueError(
                f"Invalid response format from Director for variable {var_name}: {data}"
            )
        value = json_dict[0].get("value")
        if value == "Undefined":
            return None
        return value

    async def get_all_item_variable_value(
        self, var_name: str | list | tuple | set
    ) -> list[dict[str, Any]]:
        """Returns a list of dictionaries with the values of the specified variable
        for all items that have it.

        Parameters:
            `var_name` - The Control4 variable name or names.
        """
        if isinstance(var_name, (tuple, list, set)):
            var_name = ",".join(var_name)

        data = await self.send_get_request(
            f"/api/v1/items/variables?varnames={var_name}"
        )
        if data == "[]":
            raise ValueError(
                f"Empty response received from Director! The variable {var_name} "
                f"doesn't seem to exist for any items."
            )
        json_dict = json.loads(data)
        for item in json_dict:
            if item.get("value") == "Undefined":
                item["value"] = None
        return json_dict

    async def get_item_commands(self, item_id: int) -> list[dict]:
        """Returns the commands available for the specified item.

        Parameters:
            `item_id` - The Control4 item ID.
        """
        data = await self.send_get_request(f"/api/v1/items/{item_id}/commands")
        return json.loads(data)

    async def get_item_network(self, item_id: int) -> list[dict]:
        """Returns the network information for the specified item.

        Parameters:
            `item_id` - The Control4 item ID.
        """
        data = await self.send_get_request(f"/api/v1/items/{item_id}/network")
        return json.loads(data)

    async def get_item_bindings(self, item_id: int) -> list[dict]:
        """Returns the bindings information for the specified item.

        Parameters:
            `item_id` - The Control4 item ID.
        """
        data = await self.send_get_request(f"/api/v1/items/{item_id}/bindings")
        return json.loads(data)

    async def get_ui_configuration(self) -> dict:
        """Returns a dictionary of the Control4 App UI Configuration enumerating
        rooms and capabilities

        Returns:

            {
             "experiences": [
                {
                 "type": "watch",
                 "sources": {
                    "source": [
                     {
                      "id": 59,
                      "type": "HDMI"
                     },
                     {
                      "id": 946,
                      "type": "HDMI"
                     },
                     {
                      "id": 950,
                      "type": "HDMI"
                     },
                     {
                      "id": 33,
                      "type": "VIDEO_SELECTION"
                     }
                    ]
                },
                 "active": false,
                 "room_id": 9,
                 "username": "primaryuser"
                },
                {
                 "type": "listen",
                 "sources": {
                    "source": [
                    {
                     "id": 298,
                     "type": "DIGITAL_AUDIO_SERVER",
                     "name": "My Music"
                    },
                    {
                     "id": 302,
                     "type": "AUDIO_SELECTION",
                     "name": "Stations"
                    },
                    {
                     "id": 306,
                     "type": "DIGITAL_AUDIO_SERVER",
                     "name": "ShairBridge"
                    },
                    {
                     "id": 937,
                     "type": "DIGITAL_AUDIO_SERVER",
                     "name": "Spotify Connect"
                    },
                    {
                     "id": 100002,
                     "type": "DIGITAL_AUDIO_CLIENT",
                     "name": "Digital Media"
                    }
                   ]
                },
                 "active": false,
                 "room_id": 9,
                 "username": "primaryuser"
                },
                {
                 "type": "cameras",
                 "sources": {
                    "source": [
                    {
                     "id": 877,
                     "type": "Camera"
                    },
                    ...
                }
                ...
            }
        """
        data = await self.send_get_request("/api/v1/agents/ui_configuration")
        return json.loads(data)
