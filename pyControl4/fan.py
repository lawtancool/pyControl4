"""Controls Control4 Fan devices."""

from __future__ import annotations

from pyControl4 import C4Entity


class C4Fan(C4Entity):
    # ------------------------
    # Fan State Getters
    # ------------------------

    async def get_state(self) -> bool | None:
        """
        Returns the current power state of the fan.

        Returns:
            bool: True if the fan is on, False otherwise.
        """
        value = await self.director.get_item_variable_value(self.item_id, "IS_ON")
        if value is None:
            return None
        return bool(value)

    async def get_speed(self) -> int | None:
        """
        Returns the current speed of the fan controller.

        Valid speed values:
            0 - Off
            1 - Low
            2 - Medium
            3 - Medium High
            4 - High

        Note:
            Only valid for fan controllers. On non-dimmer switches,
            use `get_state()` instead.

        Returns:
            int: Current fan speed (0–4).
        """
        value = await self.director.get_item_variable_value(
            self.item_id, "CURRENT_SPEED"
        )
        if value is None:
            return None
        return int(value)

    # ------------------------
    # Fan Control Setters
    # ------------------------

    async def set_speed(self, speed: int) -> None:
        """
        Sets the fan speed or turns it off.

        Parameters:
            speed (int): Fan speed level:
                0 - Off
                1 - Low
                2 - Medium
                3 - Medium High
                4 - High
        """
        await self.director.send_post_request(
            f"/api/v1/items/{self.item_id}/commands",
            "SET_SPEED",
            {"SPEED": speed},
        )

    async def set_preset(self, preset: int) -> None:
        """
        Sets the fan's preset speed — the speed used when the fan is
        turned on without specifying speed.

        Parameters:
            preset (int): Preset fan speed level:
                0 - Off
                1 - Low
                2 - Medium
                3 - Medium High
                4 - High
        """
        await self.director.send_post_request(
            f"/api/v1/items/{self.item_id}/commands",
            "DESIGNATE_PRESET",
            {"PRESET": preset},
        )
