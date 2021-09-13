"""Controls Control4 blind devices.
"""


class C4Blind:
    def __init__(self, C4Director, item_id):
        """Creates a Control4 Blind object.

        Parameters:
            `C4Director` - A `pyControl4.director.C4Director` object that corresponds to the Control4 Director that the blind is connected to.

            `item_id` - The Control4 item ID of the blind.
        """
        self.director = C4Director
        self.item_id = item_id

    async def getBatteryLevel(self):
        """Returns the battery of a blind. We currently don't know the range or meaning."""
        value = await self.director.getItemVariableValue(self.item_id, "Battery Level")
        return int(value)

    async def getClosing(self):
        """Returns an indication of whether the blind is moving in the closed direction as a boolean
        (True=closing, False=opening). If the blind is stopped, reports the direction it last moved."""
        value = await self.director.getItemVariableValue(self.item_id, "Closing")
        return bool(value)

    async def getFullyClosed(self):
        """Returns an indication of whether the blind is fully closed as a boolean
        (True=fully closed, False=at least partially open)."""
        value = await self.director.getItemVariableValue(self.item_id, "Fully Closed")
        return bool(value)

    async def getFullyOpen(self):
        """Returns an indication of whether the blind is fully open as a boolean
        (True=fully open, False=at least partially closed)."""
        value = await self.director.getItemVariableValue(self.item_id, "Fully Open")
        return bool(value)

    async def getLevel(self):
        """Returns the level (current position) of a blind as an int 0-100.
        0 is fully closed and 100 is fully open.
        """
        value = await self.director.getItemVariableValue(self.item_id, "Level")
        return int(value)

    async def getOpen(self):
        """Returns an indication of whether the blind is open as a boolean (True=open, False=closed).
        This is true even if the blind is only partially open."""
        value = await self.director.getItemVariableValue(self.item_id, "Open")
        return bool(value)

    async def getOpening(self):
        """Returns an indication of whether the blind is moving in the open direction as a boolean
        (True=opening, False=closing). If the blind is stopped, reports the direction it last moved."""
        value = await self.director.getItemVariableValue(self.item_id, "Opening")
        return bool(value)

    async def getStopped(self):
        """Returns an indication of whether the blind is stopped as a boolean
        (True=stopped, False=moving)."""
        value = await self.director.getItemVariableValue(self.item_id, "Stopped")
        return bool(value)

    async def getTargetLevel(self):
        """Returns the target level (desired position) of a blind as an int 0-100.
         The blind will move if this is different from the current level.
        0 is fully closed and 100 is fully open.
        """
        value = await self.director.getItemVariableValue(self.item_id, "Target Level")
        return int(value)

    async def open(self):
        """Opens the blind completely."""
        await self.director.sendPostRequest(
            "/api/v1/items/{}/commands".format(self.item_id),
            "SET_LEVEL_TARGET:LEVEL_TARGET_OPEN",
            {},
        )

    async def close(self):
        """Closes the blind completely."""
        await self.director.sendPostRequest(
            "/api/v1/items/{}/commands".format(self.item_id),
            "SET_LEVEL_TARGET:LEVEL_TARGET_CLOSED",
            {},
        )

    async def setLevelTarget(self, level):
        """Sets the desired level of a blind; it will start moving towards that level.
        Level 0 is fully closed and level 100 is fully open.

        Parameters:
            `level` - (int) 0-100
        """
        await self.director.sendPostRequest(
            "/api/v1/items/{}/commands".format(self.item_id),
            "SET_LEVEL_TARGET",
            {"LEVEL_TARGET": level},
        )

    async def stop(self):
        """Stops the blind if it is moving. Shortly after stopping, the target level will be
        set to the level the blind had actually reached when it stopped."""
        await self.director.sendPostRequest(
            "/api/v1/items/{}/commands".format(self.item_id),
            "STOP",
            {},
        )

    async def toggle(self):
        """Toggles the blind between open and closed. Has no effect if the blind is partially open."""
        await self.director.sendPostRequest(
            "/api/v1/items/{}/commands".format(self.item_id),
            "TOGGLE",
            {},
        )
