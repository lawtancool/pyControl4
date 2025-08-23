"""Controls Control4 Fan devices."""

from pyControl4 import C4Entity


class C4Fan(C4Entity):
    # ------------------------
    # Fan State Getters
    # ------------------------

    async def getState(self):
        """
        Returns the current power state of the fan.

        Returns:
            bool: True if the fan is on, False otherwise.
        """
        value = await self.director.getItemVariableValue(self.item_id, "IS_ON")
        return bool(value)

    async def getSpeed(self):
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
            use `getState()` instead.

        Returns:
            int: Current fan speed (0–4).
        """
        value = await self.director.getItemVariableValue(self.item_id, "CURRENT_SPEED")
        return int(value)

    # ------------------------
    # Fan Control Setters
    # ------------------------

    async def setSpeed(self, speed: int):
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
        await self.director.sendPostRequest(
            f"/api/v1/items/{self.item_id}/commands",
            "SET_SPEED",
            {"SPEED": speed},
        )

    async def setPreset(self, preset: int):
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
        await self.director.sendPostRequest(
            f"/api/v1/items/{self.item_id}/commands",
            "DESIGNATE_PRESET",
            {"PRESET": preset},
        )
