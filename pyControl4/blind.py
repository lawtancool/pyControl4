"""Controls Control4 blind devices."""

from __future__ import annotations

from pyControl4 import C4Entity


class C4Blind(C4Entity):
    async def get_battery_level(self) -> int | None:
        """Returns the battery of a blind. We currently don't know the range or
        meaning.
        """
        value = await self.director.get_item_variable_value(
            self.item_id, "Battery Level"
        )
        if value is None:
            return None
        return int(value)

    async def get_closing(self) -> bool | None:
        """Returns an indication of whether the blind is moving in the closed direction
        as a boolean (True=closing, False=opening). If the blind is stopped, reports
        the direction it last moved.
        """
        value = await self.director.get_item_variable_value(self.item_id, "Closing")
        if value is None:
            return None
        return bool(value)

    async def get_fully_closed(self) -> bool | None:
        """Returns an indication of whether the blind is fully closed as a boolean
        (True=fully closed, False=at least partially open)."""
        value = await self.director.get_item_variable_value(
            self.item_id, "Fully Closed"
        )
        if value is None:
            return None
        return bool(value)

    async def get_fully_open(self) -> bool | None:
        """Returns an indication of whether the blind is fully open as a boolean
        (True=fully open, False=at least partially closed)."""
        value = await self.director.get_item_variable_value(self.item_id, "Fully Open")
        if value is None:
            return None
        return bool(value)

    async def get_level(self) -> int | None:
        """Returns the level (current position) of a blind as an int 0-100.
        0 is fully closed and 100 is fully open.
        """
        value = await self.director.get_item_variable_value(self.item_id, "Level")
        if value is None:
            return None
        return int(value)

    async def get_open(self) -> bool | None:
        """Returns an indication of whether the blind is open as a boolean (True=open,
        False=closed). This is true even if the blind is only partially open.
        """
        value = await self.director.get_item_variable_value(self.item_id, "Open")
        if value is None:
            return None
        return bool(value)

    async def get_opening(self) -> bool | None:
        """Returns an indication of whether the blind is moving in the open direction
        as a boolean (True=opening, False=closing). If the blind is stopped, reports
        the direction it last moved.
        """
        value = await self.director.get_item_variable_value(self.item_id, "Opening")
        if value is None:
            return None
        return bool(value)

    async def get_stopped(self) -> bool | None:
        """Returns an indication of whether the blind is stopped as a boolean
        (True=stopped, False=moving)."""
        value = await self.director.get_item_variable_value(self.item_id, "Stopped")
        if value is None:
            return None
        return bool(value)

    async def get_target_level(self) -> int | None:
        """Returns the target level (desired position) of a blind as an int 0-100.
         The blind will move if this is different from the current level.
        0 is fully closed and 100 is fully open.
        """
        value = await self.director.get_item_variable_value(
            self.item_id, "Target Level"
        )
        if value is None:
            return None
        return int(value)

    async def open(self) -> None:
        """Opens the blind completely."""
        await self.director.send_post_request(
            f"/api/v1/items/{self.item_id}/commands",
            "SET_LEVEL_TARGET:LEVEL_TARGET_OPEN",
            {},
        )

    async def close(self) -> None:
        """Closes the blind completely."""
        await self.director.send_post_request(
            f"/api/v1/items/{self.item_id}/commands",
            "SET_LEVEL_TARGET:LEVEL_TARGET_CLOSED",
            {},
        )

    async def set_level_target(self, level: int) -> None:
        """Sets the desired level of a blind; it will start moving towards that level.
        Level 0 is fully closed and level 100 is fully open.

        Parameters:
            `level` - (int) 0-100
        """
        await self.director.send_post_request(
            f"/api/v1/items/{self.item_id}/commands",
            "SET_LEVEL_TARGET",
            {"LEVEL_TARGET": level},
        )

    async def stop(self) -> None:
        """Stops the blind if it is moving. Shortly after stopping, the target level
        will be set to the level the blind had actually reached when it stopped.
        """
        await self.director.send_post_request(
            f"/api/v1/items/{self.item_id}/commands",
            "STOP",
            {},
        )

    async def toggle(self) -> None:
        """Toggles the blind between open and closed. Has no effect if the blind is
        partially open.
        """
        await self.director.send_post_request(
            f"/api/v1/items/{self.item_id}/commands",
            "TOGGLE",
            {},
        )
