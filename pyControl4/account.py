"""Authenticates with the Control4 API, retrieves account and registered
controller info, and retrieves a bearer token for connecting to a Control4 Director.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

import aiohttp
import asyncio
import json
import logging

from .error_handling import check_response_for_error

AUTHENTICATION_ENDPOINT = "https://apis.control4.com/authentication/v1/rest"
CONTROLLER_AUTHORIZATION_ENDPOINT = (
    "https://apis.control4.com/authentication/v1/rest/authorization"
)
GET_CONTROLLERS_ENDPOINT = "https://apis.control4.com/account/v3/rest/accounts"
APPLICATION_KEY = "78f6791373d61bea49fdb9fb8897f1f3af193f11"

_LOGGER = logging.getLogger(__name__)


class C4Account:
    def __init__(
        self,
        username: str,
        password: str,
        session: aiohttp.ClientSession | None = None,
    ):
        """Creates a Control4 account object.

        Parameters:
            `username` - Control4 account username/email.

            `password` - Control4 account password.

            `session` - (Optional) Allows the use of an `aiohttp.ClientSession`
                object for all network requests. This session will not be closed
                by the library. If not provided, the library will open and close
                its own `ClientSession`s as needed.
        """
        self.username = username
        self.password = password
        self.session = session

    @asynccontextmanager
    async def _get_session(self) -> AsyncGenerator[aiohttp.ClientSession, None]:
        """Returns the configured session or creates a temporary one.

        If self.session is set, yields it without closing.
        Otherwise, creates and closes a temporary session.
        """
        if self.session is not None:
            yield self.session
        else:
            async with aiohttp.ClientSession() as session:
                yield session

    async def _send_account_auth_request(self) -> str:
        """Used internally to retrieve an account bearer token. Returns the entire
        JSON response from the Control4 auth API.
        """
        data_dict = {
            "clientInfo": {
                "device": {
                    "deviceName": "pyControl4",
                    "deviceUUID": "0000000000000000",
                    "make": "pyControl4",
                    "model": "pyControl4",
                    "os": "Android",
                    "osVersion": "10",
                },
                "userInfo": {
                    "applicationKey": APPLICATION_KEY,
                    "password": self.password,
                    "userName": self.username,
                },
            }
        }
        async with self._get_session() as session:
            async with asyncio.timeout(10):
                async with session.post(
                    AUTHENTICATION_ENDPOINT, json=data_dict
                ) as resp:
                    text = await resp.text()
                    await check_response_for_error(text)
                    return text

    async def _send_account_get_request(self, uri: str) -> str:
        """Used internally to send GET requests to the Control4 API,
        authenticated with the account bearer token. Returns the entire JSON
        response from the Control4 auth API.

        Parameters:
            `uri` - Full URI to send GET request to.
        """
        try:
            headers = {"Authorization": f"Bearer {self.account_bearer_token}"}
        except AttributeError:
            msg = (
                "The account bearer token is missing. "
                "Is your username/password correct?"
            )
            _LOGGER.error(msg)
            raise
        async with self._get_session() as session:
            async with asyncio.timeout(10):
                async with session.get(uri, headers=headers) as resp:
                    text = await resp.text()
                    await check_response_for_error(text)
                    return text

    async def _send_controller_auth_request(self, controller_common_name: str) -> str:
        """Used internally to retrieve an director bearer token. Returns the
        entire JSON response from the Control4 auth API.

        Parameters:
            `controller_common_name`: Common name of the controller.
                See `get_account_controllers()` for details.
        """
        try:
            headers = {"Authorization": f"Bearer {self.account_bearer_token}"}
        except AttributeError:
            msg = (
                "The account bearer token is missing. "
                "Is your username/password correct?"
            )
            _LOGGER.error(msg)
            raise
        data_dict = {
            "serviceInfo": {
                "commonName": controller_common_name,
                "services": "director",
            }
        }
        async with self._get_session() as session:
            async with asyncio.timeout(10):
                async with session.post(
                    CONTROLLER_AUTHORIZATION_ENDPOINT,
                    headers=headers,
                    json=data_dict,
                ) as resp:
                    text = await resp.text()
                    await check_response_for_error(text)
                    return text

    async def get_account_bearer_token(self) -> str:
        """Gets an account bearer token for making Control4 online API requests."""
        data = await self._send_account_auth_request()
        json_dict = json.loads(data)
        try:
            self.account_bearer_token = json_dict["authToken"]["token"]
            return self.account_bearer_token
        except KeyError:
            msg = (
                "Did not receive an account bearer token. "
                "Is your username/password correct?"
            )
            _LOGGER.error(msg + data)
            raise

    async def get_account_controllers(self) -> dict:
        """Returns a dictionary of the information for all controllers registered
        to an account.

        Returns:
            ```
            {
                "controllerCommonName": "control4_MODEL_MACADDRESS",
                "href": "https://apis.control4.com/account/v3/rest/accounts/000000",
                "name": "Name"
            }
            ```
        """
        data = await self._send_account_get_request(GET_CONTROLLERS_ENDPOINT)
        json_dict = json.loads(data)
        try:
            return json_dict["account"]
        except KeyError:
            msg = "Did not receive account information from the Control4 API."
            _LOGGER.error(msg + " Response: " + data)
            raise

    async def get_controller_info(self, controller_href: str) -> dict:
        """Returns a dictionary of the information of a specific controller.

        Parameters:
            `controller_href` - The API `href` of the controller (get this from
                the output of `get_account_controllers()`)

        Returns:
            ```
            {
                'allowsPatching': True,
                'allowsSupport': False,
                'blockNotifications': False,
                'controllerCommonName': 'control4_MODEL_MACADDRESS',
                'controller': {
                    'href': 'https://apis.control4.com/account/v3/rest/accounts/000000/controller'  # noqa: E501
                },
                'created': '2017-08-26T18:33:31Z',
                'dealer': {
                    'href': 'https://apis.control4.com/account/v3/rest/dealers/12345'
                },
                'enabled': True,
                'hasLoggedIn': True,
                'href': 'https://apis.control4.com/account/v3/rest/accounts/000000',
                'id': 000000,
                'lastCheckIn': '2020-06-13T21:52:34Z',
                'licenses': {
                    'href': 'https://apis.control4.com/account/v3/rest/accounts/000000/licenses'  # noqa: E501
                },
                'modified': '2020-06-13T21:52:34Z',
                'name': 'Name',
                'provisionDate': '2017-08-26T18:35:11Z',
                'storage': {
                    'href': 'https://apis.control4.com/storage/v1/rest/accounts/000000'
                },
                'type': 'Consumer',
                'users': {
                    'href': 'https://apis.control4.com/account/v3/rest/accounts/000000/users'  # noqa: E501
                }
            }
            ```
        """
        data = await self._send_account_get_request(controller_href)
        json_dict = json.loads(data)
        return json_dict

    async def get_controller_os_version(self, controller_href: str) -> str:
        """Returns the OS version of a controller as a string.

        Parameters:
            `controller_href` - The API `href` of the controller (get this from
                the output of `get_account_controllers()`)
        """
        data = await self._send_account_get_request(controller_href + "/controller")
        json_dict = json.loads(data)
        try:
            return json_dict["osVersion"]
        except KeyError:
            msg = "Did not receive OS version from the Control4 API."
            _LOGGER.error(msg + " Response: " + data)
            raise

    async def get_director_bearer_token(self, controller_common_name: str) -> dict:
        """Returns a dictionary with a director bearer token for making Control4
        Director API requests, and its time valid in seconds (usually 86400 seconds)

        Parameters:
            `controller_common_name`: Common name of the controller.
                See `get_account_controllers()` for details.
        """
        data = await self._send_controller_auth_request(controller_common_name)
        json_dict = json.loads(data)
        try:
            auth_token = json_dict.get("authToken", {})
            token = auth_token.get("token")
            valid_seconds = auth_token.get("validSeconds")
            if token is None or valid_seconds is None:
                raise KeyError("Missing token or validSeconds in authToken")
            return {"token": token, "validSeconds": valid_seconds}
        except KeyError:
            msg = "Did not receive a director bearer token from the Control4 API."
            _LOGGER.error(msg + " Response: " + data)
            raise
