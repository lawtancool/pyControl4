"""Controls Control4 Relay devices. These can include locks, and potentially other
types of devices.
"""

from __future__ import annotations

from pyControl4 import C4Entity


class C4Relay(C4Entity):
    async def get_relay_state(self) -> int | None:
        """Returns the current state of the relay.

        For locks, `0` means locked and `1` means unlocked.
        For relays in general, `0` probably means open and `1` probably means closed.
        """

        value = await self.director.get_item_variable_value(self.item_id, "RelayState")
        if value is None:
            return None
        return int(value)

    async def get_relay_state_verified(self) -> bool | None:
        """Returns True if Relay is functional.

        Notes:
            I think this is just used to verify that the relay is functional,
            not 100% sure though.
        """
        value = await self.director.get_item_variable_value(
            self.item_id, "StateVerified"
        )
        if value is None:
            return None
        return bool(value)

    async def open(self) -> None:
        """Set the relay to its open state.

        Example description JSON for this command from the director:
        ```
        {
          "display": "Lock the Front › Door Lock",
          "command": "OPEN",
          "deviceId": 307
        }
        ```
        """

        await self.director.send_post_request(
            f"/api/v1/items/{self.item_id}/commands",
            "OPEN",
            {},
        )

    async def close(self) -> None:
        """Set the relay to its closed state.

        Example description JSON for this command from the director:
        ```
        {
          "display": "Unlock the Front › Door Lock",
          "command": "CLOSE",
          "deviceId": 307
        }
        ```
        """

        await self.director.send_post_request(
            f"/api/v1/items/{self.item_id}/commands",
            "CLOSE",
            {},
        )

    async def toggle(self) -> None:
        """Toggles the relay state.

        Example description JSON for this command from the director:
        ```
        {
          "display": "Toggle the Front › Door Lock",
          "command": "TOGGLE",
          "deviceId": 307
        }
        ```
        """

        await self.director.send_post_request(
            f"/api/v1/items/{self.item_id}/commands",
            "TOGGLE",
            {},
        )
