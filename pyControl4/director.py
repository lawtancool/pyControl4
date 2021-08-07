"""Handles communication with a Control4 Director, and provides functions for
   getting details about items on the Director.
"""
import aiohttp
import async_timeout
import json
import socketio
import logging

from .error_handling import checkResponseForError

_LOGGER = logging.getLogger(__name__)


class C4DirectorNamespace(socketio.AsyncClientNamespace):
    def __init__(self, *args, **kwargs):
        self.url = kwargs.pop("url")
        self.token = kwargs.pop("token")
        self.callback = kwargs.pop("callback")
        super().__init__(*args, **kwargs)
        self.uri = "/api/v1/items/datatoui"
        self.subscriptionId = None
        self.connected = False

    def on_connect(self):
        _LOGGER.debug("C4 Director socket.io connection established!")

    def on_disconnect(self):
        self.connected = False
        self.subscriptionId = None
        _LOGGER.debug("C4 Director socket.io disconnected.")

    async def trigger_event(self, event, *args):
        if event == "subscribe":
            await self.on_subscribe(*args)
        elif event == "connect":
            self.on_connect()
        elif event == "disconnect":
            self.on_disconnect()
        elif event == "clientId":
            await self.on_clientId(*args)
        elif event == self.subscriptionId:
            msg = args[0]
            if "status" in msg:
                _LOGGER.debug(
                    f'Status message received from directory: {msg["status"]}'
                )
                await self.emit("2")
            else:
                await self.callback(args[0])

    async def on_clientId(self, clientId):
        await self.emit("2probe")
        if not self.connected and not self.subscriptionId:
            _LOGGER.debug("Fetching subscriptionID from C4")
            async with aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(verify_ssl=False)
            ) as session:
                with async_timeout.timeout(10):
                    async with session.get(
                        self.url + self.uri,
                        params={"JWT": self.token, "SubscriptionClient": clientId},
                    ) as resp:
                        await checkResponseForError(await resp.text())
                        data = await resp.json()
                        self.connected = True
                        self.subscriptionId = data["subscriptionId"]
                        await self.emit("startSubscription", self.subscriptionId)

    async def on_subscribe(self, message):
        await self.message(message)


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
        self.base_url = "https://{}".format(ip)
        self.wss_url = "wss://{}".format(ip)
        self.headers = {"Authorization": "Bearer {}".format(director_bearer_token)}
        self.director_bearer_token = director_bearer_token
        self.session = session_no_verify_ssl

        # Keep track of the device callbacks within the director
        self._device_callbacks = dict()

    async def callback(self, message):
        if "status" in message:
            _LOGGER.debug(f'Subscription {message["status"]}')
            return True
        if isinstance(message, list):
            for m in message:
                await self._process_message(m)
        else:
            await self._process_message(message)

    def add_device_callback(self, device, device_callback):
        """Register a device callback."""

        _LOGGER.debug("Subscribing to updates for device_id: %s", device)

        self._device_callbacks[device] = device_callback

    async def _process_message(self, message):
        """Process in the incoming event message"""
        _LOGGER.debug(message)
        try:
            c = self._device_callbacks[message["iddevice"]]
        except KeyError:
            _LOGGER.debug("No Callback for device id {}".format(message["iddevice"]))
            return True

        if isinstance(message, list):
            for m in message:
                await c(message["iddevice"], m)
        else:
            await c(message["iddevice"], message)

    async def sio_connect(self):
        """Start SocketIO Connection and listen"""
        sio = socketio.AsyncClient(ssl_verify=False)
        sio.register_namespace(
            C4DirectorNamespace(
                token=self.director_bearer_token,
                url=self.base_url,
                callback=self.callback,
            )
        )
        await sio.connect(
            self.wss_url,
            transports=["websocket"],
            auth={"JWT": self.director_bearer_token},
        )

    def remove_all_device_callbacks(self, device):
        """Unregister all callbacks for a device"""
        self._device_callbacks[device].clear()

    async def sendGetRequest(self, uri):
        """Sends a GET request to the specified API URI.
        Returns the Director's JSON response as a string.

        Parameters:
            `uri` - The API URI to send the request to. Do not include the IP
                    address of the Director.
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
                    try:
                        await checkResponseForError(await resp.text())
                    except KeyError as err:
                        _LOGGER.debug(str(err))
                        _LOGGER.exception(await resp.text())
                        raise
                    return await resp.text()

    async def sendPostRequest(self, uri, command, params, async_variable=True):
        """Sends a POST request to the specified API URI. Used to send commands
           to the Director.
        Returns the Director's JSON response as a string.

        Parameters:
            `uri` - The API URI to send the request to. Do not include the IP
                    address of the Director.

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

    async def getAllItemsByCategory(self, category, query_string=None):
        """Returns a JSON list of items related to a particular category

        Parameters:
            `category` - Control4 Category Name: controllers, comfort, lights,
                         cameras, sensors, audio_video,
                         motorization, thermostats, motors,
                         control4_remote_hub,
                         outlet_wireless_dimmer, voice-scene
            `query_string` - Query to limit devices in category
                             (not implemented yet)
        """
        return_list = await self.sendGetRequest(
            "/api/v1/categories/{}".format(category)
        )
        return return_list

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
        """Returns the value of the specified variable for the
        specified item as a string.

        Parameters:
            `item_id` - The Control4 item ID.

            `var_name` - The Control4 variable name.
        """
        data = await self.sendGetRequest(
            "/api/v1/items/{}/variables?varnames={}".format(item_id, var_name)
        )
        if data == "[]":
            raise ValueError(
                "Empty response recieved from Director! The variable {} \
                    doesn't seem to exist for item {}.".format(
                    var_name, item_id
                )
            )
        jsonDictionary = json.loads(data)
        return jsonDictionary[0]["value"]

    async def getAllItemVariableValue(self, var_name):
        """Returns a dictionary with the values of the specified variable
        for all items that have it.

        Parameters:
            `var_name` - The Control4 variable name.
        """
        data = await self.sendGetRequest(
            "/api/v1/items/variables?varnames={}".format(var_name)
        )
        if data == "[]":
            raise ValueError(
                "Empty response recieved from Director! The variable {} \
                    doesn't seem to exist for any items.".format(
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

    async def _execute_callback(self, callback, *args, **kwargs):
        """Callback with some data capturing any excpetions"""
        try:
            self.sio.emit("ping")
            await callback(*args, **kwargs)
        except Exception as exc:
            _LOGGER.warning("Captured exception during callback: {}".format(str(exc)))
