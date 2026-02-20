"""Controls Control4 Light devices."""

from __future__ import annotations

from pyControl4 import C4Entity


class C4Light(C4Entity):
    async def get_level(self) -> int | None:
        """Returns the level of a dimming-capable light as an int 0-100.
        Will cause an error if called on a non-dimmer switch. Use `get_state()` instead.
        """
        value = await self.director.get_item_variable_value(self.item_id, "LIGHT_LEVEL")
        if value is None:
            return None
        return int(value)

    async def get_state(self) -> bool | None:
        """Returns the power state of a dimmer or switch as a boolean (True=on,
        False=off).
        """
        value = await self.director.get_item_variable_value(self.item_id, "LIGHT_STATE")
        if value is None:
            return None
        return bool(value)

    async def set_level(self, level: int) -> None:
        """Sets the light level of a dimmer or turns on/off a switch.
        Any `level > 0` will turn on a switch, and `level = 0` will turn off a switch.

        Parameters:
            `level` - (int) 0-100
        """
        await self.director.send_post_request(
            f"/api/v1/items/{self.item_id}/commands",
            "SET_LEVEL",
            {"LEVEL": level},
        )

    async def ramp_to_level(self, level: int, time: int) -> None:
        """Ramps the light level of a dimmer over time.
        Any `level > 0` will turn on a switch, and `level = 0` will turn off a switch.

        Parameters:
            `level` - (int) 0-100

            `time` - (int) Duration in milliseconds
        """
        await self.director.send_post_request(
            f"/api/v1/items/{self.item_id}/commands",
            "RAMP_TO_LEVEL",
            {"LEVEL": level, "TIME": time},
        )

    async def set_color_xy(
        self, x: float, y: float, *, rate: int | None = None
    ) -> None:
        """Sends SET_COLOR_TARGET with xy"""
        params = {
            "LIGHT_COLOR_TARGET_X": float(x),
            "LIGHT_COLOR_TARGET_Y": float(y),
            "LIGHT_COLOR_TARGET_MODE": 0,
        }
        if rate is not None:
            params["RATE"] = int(rate)

        await self.director.send_post_request(
            f"/api/v1/items/{self.item_id}/commands",
            "SET_COLOR_TARGET",
            params,
        )

    async def set_color_temperature(
        self, kelvin: int, *, rate: int | None = None
    ) -> None:
        params = {
            "LIGHT_COLOR_TARGET_COLOR_CORRELATED_TEMPERATURE": int(kelvin),
            "LIGHT_COLOR_TARGET_MODE": 1,
        }
        if rate is not None:
            params["RATE"] = int(rate)

        await self.director.send_post_request(
            f"/api/v1/items/{self.item_id}/commands",
            "SET_COLOR_TARGET",
            params,
        )
