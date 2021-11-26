"""Controls Control4 Relay devices. These can include locks, and potentially other types of devices.
"""


class C4Relay:
    def __init__(self, C4Director, item_id):
        """Creates a Control4 Relay object.

        Parameters:
            `C4Director` - A `pyControl4.director.C4Director` object that
            corresponds to the Control4 Director that the Relay is connected to.

            `item_id` - The Control4 item ID of the Relay.
        """
        self.director = C4Director
        self.item_id = item_id

    async def getRelayState(self):
        """Returns the current state of the relay.

        For locks, `0` means locked and `1` means unlocked.
        For relays in general, `0` probably means open and `1` probably means closed.
        """

        return await self.director.getItemVariableValue(self.item_id, "RelayState")

    async def getRelayStateVerified(self):
        """Returns True if Relay is functional.

        Notes:
            I think this is just used to verify that the relay is functional,
            not 100% sure though.
        """
        return bool(
            await self.director.getItemVariableValue(self.item_id, "StateVerified")
        )

    async def open(self):
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

        await self.director.sendPostRequest(
            "/api/v1/items/{}/commands".format(self.item_id),
            "OPEN",
            {},
        )

    async def close(self):
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

        await self.director.sendPostRequest(
            "/api/v1/items/{}/commands".format(self.item_id),
            "CLOSE",
            {},
        )

    async def toggle(self):
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

        await self.director.sendPostRequest(
            "/api/v1/items/{}/commands".format(self.item_id),
            "TOGGLE",
            {},
        )
