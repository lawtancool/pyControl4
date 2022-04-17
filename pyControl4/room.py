"""Controls Control4 Room devices.
"""


class C4Room:
    def __init__(self, C4Director, item_id):
        """Creates a Control4 Room object.

        Parameters:
            `C4Director` - A `pyControl4.director.C4Director` object that corresponds to the Control4 Director that the light is connected to.

            `item_id` - The Control4 item ID of the room.
        """
        self.director = C4Director
        self.item_id = item_id

    async def isRoomHidden(self) -> bool:
        """Returns True if the room is hidden from the end-user"""
        value = await self.director.getItemVariableValue(self.item_id, "ROOM_HIDDEN")
        return int(value) != 0

    async def isOn(self) -> bool:
        """Returns True/False if the room is "ON" from the director's perspective
        """
        value = await self.director.getItemVariableValue(self.item_id, "POWER_STATE")
        return int(value) != 0

    async def setRoomOff(self):
        """ Turn the room "OFF" """
        await self.director.sendPostRequest(
            "/api/v1/items/{}/commands".format(self.item_id),
            "ROOM_OFF",
            {},
        )

    async def getVolume(self) -> int:
        """Returns the current volume for the room from 0-100"""
        value = await self.director.getItemVariableValue(self.item_id, "CURRENT_VOLUME")
        return int(value)

    async def isMuted(self) -> bool:
        """Returns True if the room is muted"""
        value = await self.director.getItemVariableValue(self.item_id, "IS_MUTED")
        return int(value) != 0

    async def setMute(self, muted: bool):
        """ Mute/Unmute the room """
        await self.director.sendPostRequest(
            "/api/v1/items/{}/commands".format(self.item_id),
            "MUTE_ON" if muted else "MUTE_OFF",
            {},
        )

    async def toggleMute(self):
        """ Toggle the current mute state for the room """
        await self.director.sendPostRequest(
            "/api/v1/items/{}/commands".format(self.item_id),
            "MUTE_TOGGLE",
            {},
        )

    async def setVolume(self, volume: int):
        """ Set the room volume, 0-100 """
        await self.director.sendPostRequest(
            "/api/v1/items/{}/commands".format(self.item_id),
            "SET_VOLUME_LEVEL",
            {"LEVEL": level},
        )