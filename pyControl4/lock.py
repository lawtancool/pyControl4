class C4Lock:
    def __init__(self, C4Director, item_id):
        """Creates a Control4 Lock object.

        Parameters:
            `C4Director` - A `pyControl4Ex.director.C4Director` object that
            corresponds to the Control4 Director that the Lock is connected to.

            `item_id` - The Control4 item ID of the Lock.
        """
        self.director = C4Director
        self.item_id = item_id

    async def getLockState(self):
        """Returns True if it is currently Locked or False if it is Unlocked

        Notes:
            Relay State 0 == Locked
            Relay State 1 == Unlocked
        """
        return not bool(
            await self.director.getItemVariableValue(self.item_id, "RelayState")
        )

    async def getLockStateVerified(self):
        """Returns True if Lock Relay is functional

        Notes:
            I think this is just used to verify that the relay is functional,
            not 100% sure though.
        """
        return bool(
            await self.director.getItemVariableValue(self.item_id, "StateVerified")
        )

    async def lock(self):
        """Locks the current lock

         I assume the 'OPEN' command is referring to setting the relay to it's
         Open state which actually engages the lock
        Example Json for this command from the director:
        {
          "display": "Lock the Front › Door Lock",
          "command": "OPEN",
          "deviceId": 307
        }
        """
        await self.director.sendPostRequest(
            self.director.COMMANDS_ENDPOINT.format(self.item_id),
            "OPEN",
            {},
        )

    async def unlock(self):
        """Unlocks the current lock

         I assume the 'CLOSE' command is referring to setting the relay to it's
         Closed state which actually disengages the lock
        Example Json for this command from the director:
        {
          "display": "Unlock the Front › Door Lock",
          "command": "CLOSE",
          "deviceId": 307
        }
        """
        await self.director.sendPostRequest(
            self.director.COMMANDS_ENDPOINT.format(self.item_id),
            "CLOSE",
            {},
        )

    async def toggle(self):
        """Toggles the current lock

        Example Json for this command from the director:
        {
          "display": "Toggle the Front › Door Lock",
          "command": "TOGGLE",
          "deviceId": 307
        }
        """
        await self.director.sendPostRequest(
            self.director.COMMANDS_ENDPOINT.format(self.item_id),
            "TOGGLE",
            {},
        )
