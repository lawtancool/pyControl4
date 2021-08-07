"""Authenticates with the Control4 API, retrieves account and registered
controller info, and retrieves a bearer token for connecting to a Control4 Director.
"""
import aiohttp
import async_timeout
import json
import logging
import datetime

from .error_handling import checkResponseForError

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
        username,
        password,
        session: aiohttp.ClientSession = None,
    ):
        """Creates a Control4 account object.

        Parameters:
            `username` - Control4 account username/email.

            `password` - Control4 account password.

            `session` - (Optional) Allows the use of an `aiohttp.ClientSession` object for all network requests. This session will not be closed by the library.
            If not provided, the library will open and close its own `ClientSession`s as needed.
        """
        self.username = username
        self.password = password
        self.session = session

    async def __sendAccountAuthRequest(self):
        """Used internally to retrieve an account bearer token. Returns the entire
        JSON response from the Control4 auth API.
        """
        dataDictionary = {
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
        if self.session is None:
            async with aiohttp.ClientSession() as session:
                with async_timeout.timeout(10):
                    async with session.post(
                        AUTHENTICATION_ENDPOINT, json=dataDictionary
                    ) as resp:
                        await checkResponseForError(await resp.text())
                        return await resp.text()
        else:
            with async_timeout.timeout(10):
                async with self.session.post(
                    AUTHENTICATION_ENDPOINT, json=dataDictionary
                ) as resp:
                    await checkResponseForError(await resp.text())
                    return await resp.text()

    async def __sendAccountGetRequest(self, uri):
        """Used internally to send GET requests to the Control4 API,
        authenticated with the account bearer token. Returns the entire JSON
        response from the Control4 auth API.

        Parameters:
            `uri` - Full URI to send GET request to.
        """
        try:
            headers = {"Authorization": "Bearer {}".format(self.account_bearer_token)}
        except AttributeError:
            msg = "The account bearer token is missing - was your username/password correct? "
            _LOGGER.error(msg)
            raise
        if self.session is None:
            async with aiohttp.ClientSession() as session:
                with async_timeout.timeout(10):
                    async with session.get(uri, headers=headers) as resp:
                        await checkResponseForError(await resp.text())
                        return await resp.text()
        else:
            with async_timeout.timeout(10):
                async with self.session.get(uri, headers=headers) as resp:
                    await checkResponseForError(await resp.text())
                    return await resp.text()

    async def __sendControllerAuthRequest(self, controller_common_name):
        """Used internally to retrieve an director bearer token. Returns the
        entire JSON response from the Control4 auth API.

        Parameters:
            `controller_common_name`: Common name of the controller. See `getAccountControllers()` for details.
        """
        try:
            headers = {"Authorization": "Bearer {}".format(self.account_bearer_token)}
        except AttributeError:
            msg = "The account bearer token is missing - was your username/password correct? "
            _LOGGER.error(msg)
            raise
        dataDictionary = {
            "serviceInfo": {
                "commonName": controller_common_name,
                "services": "director",
            }
        }
        if self.session is None:
            async with aiohttp.ClientSession() as session:
                with async_timeout.timeout(10):
                    async with session.post(
                        CONTROLLER_AUTHORIZATION_ENDPOINT,
                        headers=headers,
                        json=dataDictionary,
                    ) as resp:
                        await checkResponseForError(await resp.text())
                        return await resp.text()
        else:
            with async_timeout.timeout(10):
                async with self.session.post(
                    CONTROLLER_AUTHORIZATION_ENDPOINT,
                    headers=headers,
                    json=dataDictionary,
                ) as resp:
                    await checkResponseForError(await resp.text())
                    return await resp.text()

    async def getAccountBearerToken(self):
        """Gets an account bearer token for making Control4 online API requests."""
        data = await self.__sendAccountAuthRequest()
        jsonDictionary = json.loads(data)
        try:
            self.account_bearer_token = jsonDictionary["authToken"]["token"]
            return self.account_bearer_token
        except KeyError:
            msg = "Did not recieve an account bearer token. Is your username/password correct? "
            _LOGGER.error(msg + data)
            raise

    async def getAccountControllers(self):
        """Returns a dictionary of the information for all controllers registered to an account.

        Returns:
            ```
            {
                "controllerCommonName": "control4_MODEL_MACADDRESS",
                "href": "https://apis.control4.com/account/v3/rest/accounts/000000",
                "name": "Name"
            }
            ```
        """
        data = await self.__sendAccountGetRequest(GET_CONTROLLERS_ENDPOINT)
        jsonDictionary = json.loads(data)
        return jsonDictionary["account"]

    async def getControllerInfo(self, controller_href):
        """Returns a dictionary of the information of a specific controller.

        Parameters:
            `controller_href` - The API `href` of the controller (get this from the output of `getAccountControllers()`)

        Returns:
            ```
            {
                'allowsPatching': True,
                'allowsSupport': False,
                'blockNotifications': False,
                'controllerCommonName': 'control4_MODEL_MACADDRESS',
                'controller': {
                    'href': 'https://apis.control4.com/account/v3/rest/accounts/000000/controller'
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
                    'href': 'https://apis.control4.com/account/v3/rest/accounts/000000/licenses'
                },
                'modified': '2020-06-13T21:52:34Z',
                'name': 'Name',
                'provisionDate': '2017-08-26T18:35:11Z',
                'storage': {
                    'href': 'https://apis.control4.com/storage/v1/rest/accounts/000000'
                },
                'type': 'Consumer',
                'users': {
                    'href': 'https://apis.control4.com/account/v3/rest/accounts/000000/users'
                }
            }
            ```
        """
        data = await self.__sendAccountGetRequest(controller_href)
        jsonDictionary = json.loads(data)
        return jsonDictionary

    async def getControllerOSVersion(self, controller_href):
        """Returns the OS version of a controller as a string.

        Parameters:
            `controller_href` - The API `href` of the controller (get this from the output of `getAccountControllers()`)
        """
        data = await self.__sendAccountGetRequest(controller_href + "/controller")
        jsonDictionary = json.loads(data)
        return jsonDictionary["osVersion"]

    async def getDirectorBearerToken(self, controller_common_name):
        """Returns a dictionary with a director bearer token for making Control4 Director API requests, and its expiry time (generally 86400 seconds after current time)

        Parameters:
            `controller_common_name`: Common name of the controller. See `getAccountControllers()` for details.
        """
        data = await self.__sendControllerAuthRequest(controller_common_name)
        jsonDictionary = json.loads(data)
        token_expiration = datetime.datetime.now() + datetime.timedelta(
            seconds=jsonDictionary["authToken"]["validSeconds"]
        )
        return {
            "token": jsonDictionary["authToken"]["token"],
            "token_expiration": token_expiration,
        }
