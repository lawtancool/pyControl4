"""Handles Websocket connections to a Control4 Director, allowing for real-time updates using callbacks."""

import aiohttp
import async_timeout
import socketio_v4 as socketio
import logging

from .error_handling import checkResponseForError

_LOGGER = logging.getLogger(__name__)


class _C4DirectorNamespace(socketio.AsyncClientNamespace):
    def __init__(self, *args, **kwargs):
        self.url = kwargs.pop("url")
        self.token = kwargs.pop("token")
        self.callback = kwargs.pop("callback")
        self.session = kwargs.pop("session")
        self.connect_callback = kwargs.pop("connect_callback")
        self.disconnect_callback = kwargs.pop("disconnect_callback")
        super().__init__(*args, **kwargs)
        self.uri = "/api/v1/items/datatoui"
        self.subscriptionId = None
        self.connected = False

    async def on_connect(self):
        _LOGGER.debug("Control4 Director socket.io connection established!")
        if self.connect_callback is not None:
            await self.connect_callback()

    async def on_disconnect(self):
        self.connected = False
        self.subscriptionId = None
        _LOGGER.debug("Control4 Director socket.io disconnected.")
        if self.disconnect_callback is not None:
            await self.disconnect_callback()

    async def trigger_event(self, event, *args):
        if event == "subscribe":
            await self.on_subscribe(*args)
        elif event == "connect":
            await self.on_connect()
        elif event == "disconnect":
            await self.on_disconnect()
        elif event == "clientId":
            await self.on_clientId(*args)
        elif event == self.subscriptionId:
            msg = args[0]
            if "status" in msg:
                _LOGGER.debug(f'Status message received from Director: {msg["status"]}')
                await self.emit("2")
            else:
                await self.callback(args[0])

    async def on_clientId(self, clientId):
        await self.emit("2probe")
        if not self.connected and not self.subscriptionId:
            _LOGGER.debug("Fetching subscriptionID from Control4")
            if self.session is None:
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
            else:
                with async_timeout.timeout(10):
                    async with self.session.get(
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


class C4Websocket:
    def __init__(
        self,
        ip,
        session_no_verify_ssl: aiohttp.ClientSession = None,
        connect_callback=None,
        disconnect_callback=None,
    ):
        """Creates a Control4 Websocket object.

        Parameters:
            `ip` - The IP address of the Control4 Director/Controller.

            `session` - (Optional) Allows the use of an
                        `aiohttp.ClientSession` object
                        for all network requests. This
                        session will not be closed by the library.
                        If not provided, the library will open and
                        close its own `ClientSession`s as needed.

            `connect_callback` - (Optional) A callback to be called when the Websocket connection is opened or reconnected after a network error.

            `disconnect_callback` - (Optional) A callback to be called when the Websocket connection is lost due to a network error.
        """
        self.base_url = "https://{}".format(ip)
        self.wss_url = "wss://{}".format(ip)
        self.session = session_no_verify_ssl
        self.connect_callback = connect_callback
        self.disconnect_callback = disconnect_callback

        # Keep track of the callbacks registered for each item id
        self._item_callbacks = dict()
        # Initialize self._sio to None
        self._sio = None

    @property
    def item_callbacks(self):
        """Returns a dictionary of registered item ids (key) and their callbacks (value).

        item_callbacks cannot be modified directly. Use add_item_callback() and remove_item_callback() instead.
        """
        return self._item_callbacks

    def add_item_callback(self, item_id, callback):
        """Register a callback to receive updates about an item.
        If a callback is already registered for the item, it will be overwritten with the provided callback.

        Parameters:
            `item_id` - The Control4 item ID.

            `callback` - The callback to be called when an update is received for the provided item id.
        """

        _LOGGER.debug("Subscribing to updates for item id: %s", item_id)

        self._item_callbacks[item_id] = callback

    def remove_item_callback(self, item_id):
        """Unregister callback for an item.

        Parameters:
            `item_id` - The Control4 item ID.
        """
        self._item_callbacks.pop(item_id)

    async def sio_connect(self, director_bearer_token):
        """Start WebSockets connection and listen, using the provided director_bearer_token to authenticate with the Control4 Director.
        If a connection already exists, it will be disconnected and a new connection will be created.

        This function should be called using a new token every 86400 seconds (the expiry time of the director tokens), otherwise the Control4 Director will stop sending WebSocket messages.

        Parameters:
            `director_bearer_token` - The bearer token used to authenticate with the Director. See `pyControl4.account.C4Account.getDirectorBearerToken` for how to get this.
        """
        # Disconnect previous sio object
        await self.sio_disconnect()

        self._sio = socketio.AsyncClient(ssl_verify=False)
        self._sio.register_namespace(
            _C4DirectorNamespace(
                token=director_bearer_token,
                url=self.base_url,
                callback=self._callback,
                session=self.session,
                connect_callback=self.connect_callback,
                disconnect_callback=self.disconnect_callback,
            )
        )
        await self._sio.connect(
            self.wss_url,
            transports=["websocket"],
            headers={"JWT": director_bearer_token},
        )

    async def sio_disconnect(self):
        """Disconnects the WebSockets connection, if it has been created."""
        if isinstance(self._sio, socketio.AsyncClient):
            await self._sio.disconnect()

    async def _callback(self, message):
        if "status" in message:
            _LOGGER.debug(f'Subscription {message["status"]}')
            return True
        if isinstance(message, list):
            for m in message:
                await self._process_message(m)
        else:
            await self._process_message(message)

    async def _process_message(self, message):
        """Process an incoming event message."""
        _LOGGER.debug(message)
        try:
            c = self._item_callbacks[message["iddevice"]]
        except KeyError:
            _LOGGER.debug("No Callback for device id {}".format(message["iddevice"]))
            return True

        if isinstance(message, list):
            for m in message:
                await c(message["iddevice"], m)
        else:
            await c(message["iddevice"], message)

    async def _execute_callback(self, callback, *args, **kwargs):
        """Callback with some data capturing any excpetions."""
        try:
            self.sio.emit("ping")
            await callback(*args, **kwargs)
        except Exception as exc:
            _LOGGER.warning("Captured exception during callback: {}".format(str(exc)))
