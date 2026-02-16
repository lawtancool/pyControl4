"""Controls Control4 Light devices."""

from pyControl4 import C4Entity


class C4Light(C4Entity):
    async def getLevel(self):
        """Returns the level of a dimming-capable light as an int 0-100.
        Will cause an error if called on a non-dimmer switch. Use `getState()` instead.
        """
        value = await self.director.getItemVariableValue(self.item_id, "LIGHT_LEVEL")
        if value is None:
            return None
        return int(value)

    async def getState(self):
        """Returns the power state of a dimmer or switch as a boolean (True=on, False=off)."""
        value = await self.director.getItemVariableValue(self.item_id, "LIGHT_STATE")
        if value is None:
            return None
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

    async def setColorXY(self, x: float, y: float, *, rate: int | None = None):
        """Sends SET_COLOR_TARGET with xy"""
        params = {
            "LIGHT_COLOR_TARGET_X": float(x),
            "LIGHT_COLOR_TARGET_Y": float(y),
            "LIGHT_COLOR_TARGET_MODE": 0,
        }
        if rate is not None:
            params["RATE"] = int(rate)

        await self.director.sendPostRequest(
            f"/api/v1/items/{self.item_id}/commands",
            "SET_COLOR_TARGET",
            params,
        )

    async def setColorTemperature(self, kelvin: int, *, rate: int | None = None):
        params = {
            "LIGHT_COLOR_TARGET_COLOR_CORRELATED_TEMPERATURE": int(kelvin),
            "LIGHT_COLOR_TARGET_MODE": 1,
        }
        if rate is not None:
            params["RATE"] = int(rate)

        await self.director.sendPostRequest(
            f"/api/v1/items/{self.item_id}/commands",
            "SET_COLOR_TARGET",
            params,
        )
