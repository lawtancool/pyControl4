"""Handles Websocket connections to a Control4 Director, allowing for real-time
updates using callbacks.
"""

from __future__ import annotations

from typing import Any, Callable
from types import MappingProxyType

import aiohttp
import asyncio
import socketio_v4 as socketio
import logging

from .error_handling import check_response_for_error

_LOGGER = logging.getLogger(__name__)

_NAMESPACE_URI = "/api/v1/items/datatoui"
_PROBE_MESSAGE = "2probe"
_STATUS_ACK_MESSAGE = "2"


class _C4DirectorNamespace(socketio.AsyncClientNamespace):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.url: str = kwargs.pop("url")
        self.token: str = kwargs.pop("token")
        self.callback: Callable = kwargs.pop("callback")
        self.session: aiohttp.ClientSession | None = kwargs.pop("session")
        self.connect_callback: Callable | None = kwargs.pop("connect_callback")
        self.disconnect_callback: Callable | None = kwargs.pop("disconnect_callback")
        super().__init__(*args, **kwargs)
        self.uri = _NAMESPACE_URI
        self.subscription_id: str | None = None
        self.connected: bool = False

    async def on_connect(self) -> None:
        _LOGGER.debug("Control4 Director socket.io connection established!")
        if self.connect_callback is not None:
            await self.connect_callback()

    async def on_disconnect(self) -> None:
        self.connected = False
        self.subscription_id = None
        _LOGGER.debug("Control4 Director socket.io disconnected.")
        if self.disconnect_callback is not None:
            await self.disconnect_callback()

    async def trigger_event(self, event: str, *args: Any) -> None:
        if event == "subscribe":
            await self.on_subscribe(*args)
        elif event == "connect":
            await self.on_connect()
        elif event == "disconnect":
            await self.on_disconnect()
        elif event == "clientId":
            await self.on_clientId(*args)
        elif event == self.subscription_id:
            msg = args[0]
            if "status" in msg:
                _LOGGER.debug(f'Status message received from Director: {msg["status"]}')
                await self.emit(_STATUS_ACK_MESSAGE)
            else:
                await self.callback(args[0])

    async def on_clientId(self, client_id: str) -> None:
        await self.emit(_PROBE_MESSAGE)
        if not self.connected and not self.subscription_id:
            _LOGGER.debug("Fetching subscriptionID from Control4")
            session = self.session or aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(verify_ssl=False)
            )
            try:
                async with asyncio.timeout(10):
                    async with session.get(
                        self.url + self.uri,
                        params={"JWT": self.token, "SubscriptionClient": client_id},
                    ) as resp:
                        check_response_for_error(await resp.text())
                        data = await resp.json()
                        subscription_id = data.get("subscriptionId")
                        if subscription_id is None:
                            raise ValueError(
                                "Failed to get subscription ID from Control4 Director"
                            )
                        self.connected = True
                        self.subscription_id = subscription_id
                        await self.emit("startSubscription", self.subscription_id)
            finally:
                if self.session is None:
                    await session.close()

    async def on_subscribe(self, message: Any) -> None:
        pass


class C4Websocket:
    def __init__(
        self,
        ip: str,
        session_no_verify_ssl: aiohttp.ClientSession | None = None,
        connect_callback: Callable | None = None,
        disconnect_callback: Callable | None = None,
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

            `connect_callback` - (Optional) A callback to be called when the
                Websocket connection is opened or reconnected after a network
                error.

            `disconnect_callback` - (Optional) A callback to be called when
                the Websocket connection is lost due to a network error.
        """
        self.base_url: str = f"https://{ip}"
        self.wss_url: str = f"wss://{ip}"
        self.session: aiohttp.ClientSession | None = session_no_verify_ssl
        self.connect_callback: Callable | None = connect_callback
        self.disconnect_callback: Callable | None = disconnect_callback

        self._item_callbacks: dict[int, list[Callable]] = dict()
        self._sio: socketio.AsyncClient | None = None

    @property
    def item_callbacks(self) -> MappingProxyType[int, list[Callable]]:
        """Returns a read-only view of registered item ids (key) and their
        callbacks (value). Use add_item_callback() or remove_item_callback()
        to modify callbacks.
        """
        return MappingProxyType(self._item_callbacks)

    def add_item_callback(self, item_id: int, callback: Callable) -> None:
        """Register a callback to receive updates about an item.
        Parameters:
            `item_id` - The Control4 item ID.
            `callback` - The callback to be called when an update is received
                for the provided item id.
        """
        _LOGGER.debug("Subscribing to updates for item id: %s", item_id)

        if item_id not in self._item_callbacks:
            self._item_callbacks[item_id] = []

        # Avoid duplicates
        if callback not in self._item_callbacks[item_id]:
            self._item_callbacks[item_id].append(callback)

    def remove_item_callback(
        self, item_id: int, callback: Callable | None = None
    ) -> None:
        """Unregister callback(s) for an item.
        Parameters:
            `item_id` - The Control4 item ID.
            `callback` - (Optional) Specific callback to remove. If None,
                removes all callbacks for this item_id.
        """
        if item_id not in self._item_callbacks:
            return

        if callback is None:
            # Remove all callbacks for this item_id
            del self._item_callbacks[item_id]
        else:
            # Remove a specific callback
            try:
                self._item_callbacks[item_id].remove(callback)
                # If no more callbacks, remove the entry
                if not self._item_callbacks[item_id]:
                    del self._item_callbacks[item_id]
            except ValueError:
                pass

    async def sio_connect(self, director_bearer_token: str) -> None:
        """Start WebSockets connection and listen, using the provided
        director_bearer_token to authenticate with the Control4 Director. If a
        connection already exists, it will be disconnected and a new connection
        will be created.

        This function should be called using a new token every 86400 seconds (the
        expiry time of the director tokens), otherwise the Control4 Director will
        stop sending WebSocket messages.

        Parameters:
            `director_bearer_token` - The bearer token used to authenticate
                with the Director. See
                `pyControl4.account.C4Account.getDirectorBearerToken`
                for how to get this.
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

    async def sio_disconnect(self) -> None:
        """Disconnects the WebSockets connection, if it has been created."""
        if isinstance(self._sio, socketio.AsyncClient):
            await self._sio.disconnect()

    async def _callback(self, message: Any) -> None:
        if "status" in message:
            _LOGGER.debug(f'Subscription {message["status"]}')
        if isinstance(message, list):
            for m in message:
                await self._process_message(m)
        else:
            await self._process_message(message)

    async def _process_message(self, message: Any) -> None:
        """Process an incoming event message."""
        _LOGGER.debug(message)
        device_id = message.get("iddevice") if isinstance(message, dict) else None
        if device_id is None:
            _LOGGER.debug("Received message without iddevice field")
            return

        callbacks = self._item_callbacks.get(device_id, [])
        if not callbacks:
            _LOGGER.debug(f"No Callback for device id {device_id}")
            return

        for callback in callbacks[:]:
            try:
                if isinstance(message, list):
                    for m in message:
                        await callback(device_id, m)
                else:
                    await callback(device_id, message)
            except Exception as exc:
                _LOGGER.warning(f"Captured exception during callback: {str(exc)}")
