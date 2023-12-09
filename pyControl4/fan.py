"""Controls Control4 Light devices.
"""


from pyControl4 import C4Entity


class C4Fan(C4Entity):
    async def getSpeed(self):
        """Returns the speed of a fan controller 0-4 are valid values.
        Will cause an error if called on a non-dimmer switch. Use `getState()` instead.
        0 - off, 1 - low, 2 - medium, 3 - medium high, 4 - high
        """
        value = await self.director.getItemVariableValue(self.item_id, "CURRENT_SPEED")
        return int(value)

    async def getState(self):
        """Returns the power state of thee fan as a boolean (True=on, False=off)."""
        value = await self.director.getItemVariableValue(self.item_id, "IS_ON")
        return bool(value)

    async def setSpeed(self, speed):
        """Sets the fan speed, or turns off the fan..
           speed 0 for off, 1 for low, 2 for medium, 3 for medium high, 4 for high

        Parameters:
            `speed` - (int) 0-4
        """
        await self.director.sendPostRequest(
            "/api/v1/items/{}/commands".format(self.item_id),
            "SET_SPEED",
            {"SPEED": speed},
        )
    
    async def setPreset(self, preset):
        """Sets the preset fan speed, the speed the fan goes to if you just hit on
           speed 0 for off, 1 for low, 2 for medium, 3 for medium high, 4 for high

        Parameters:
            `preset` - (int) 0-4
        """
        await self.director.sendPostRequest(
            "/api/v1/items/{}/commands".format(self.item_id),
            "DESIGNATE_PRESET",
            {"PRESET": preset},
        )
