"""Controls Control4 Light devices."""

from pyControl4 import C4Entity


class C4Light(C4Entity):
    async def getLevel(self):
        """Returns the level of a dimming-capable light as an int 0-100.
        Will cause an error if called on a non-dimmer switch. Use `getState()` instead.
        """
        value = await self.director.getItemVariableValue(self.item_id, "LIGHT_LEVEL")
        return int(value)

    async def getState(self):
        """Returns the power state of a dimmer or switch as a boolean (True=on, False=off)."""
        value = await self.director.getItemVariableValue(self.item_id, "LIGHT_STATE")
        return bool(value)

    async def setLevel(self, level):
        """Sets the light level of a dimmer or turns on/off a switch.
        Any `level > 0` will turn on a switch, and `level = 0` will turn off a switch.

        Parameters:
            `level` - (int) 0-100
        """
        await self.director.sendPostRequest(
            "/api/v1/items/{}/commands".format(self.item_id),
            "SET_LEVEL",
            {"LEVEL": level},
        )

    async def rampToLevel(self, level, time):
        """Ramps the light level of a dimmer over time.
        Any `level > 0` will turn on a switch, and `level = 0` will turn off a switch.

        Parameters:
            `level` - (int) 0-100

            `time` - (int) Duration in milliseconds
        """
        await self.director.sendPostRequest(
            "/api/v1/items/{}/commands".format(self.item_id),
            "RAMP_TO_LEVEL",
            {"LEVEL": level, "TIME": time},
        )
