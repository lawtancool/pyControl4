"""Controls Control4 Room devices."""

from pyControl4 import C4Entity


class C4Room(C4Entity):
    """
    A media-oriented view of a Control4 Room, supporting items of type="room"
    """

    async def isRoomHidden(self) -> bool:
        """Returns True if the room is hidden from the end-user"""
        value = await self.director.getItemVariableValue(self.item_id, "ROOM_HIDDEN")
        return int(value) != 0

    async def isOn(self) -> bool:
        """Returns True/False if the room is "ON" from the director's perspective"""
        value = await self.director.getItemVariableValue(self.item_id, "POWER_STATE")
        return int(value) != 0

    async def setRoomOff(self):
        """Turn the room "OFF" """
        await self.director.sendPostRequest(
            "/api/v1/items/{}/commands".format(self.item_id),
            "ROOM_OFF",
            {},
        )

    async def _setSource(self, source_id: int, audio_only: bool):
        """
        Sets the room source, turning on the room if necessary.
        If audio_only, only the current audio device is changed
        """
        await self.director.sendPostRequest(
            f"/api/v1/items/{self.item_id}/commands",
            "SELECT_AUDIO_DEVICE" if audio_only else "SELECT_VIDEO_DEVICE",
            {"deviceid": source_id},
        )

    async def setAudioSource(self, source_id: int):
        """Sets the current audio source for the room"""
        await self._setSource(source_id, audio_only=True)

    async def setVideoAndAudioSource(self, source_id: int):
        """Sets the current audio and video source for the room"""
        await self._setSource(source_id, audio_only=False)

    async def getVolume(self) -> int:
        """Returns the current volume for the room from 0-100"""
        value = await self.director.getItemVariableValue(self.item_id, "CURRENT_VOLUME")
        return int(value)

    async def isMuted(self) -> bool:
        """Returns True if the room is muted"""
        value = await self.director.getItemVariableValue(self.item_id, "IS_MUTED")
        return int(value) != 0

    async def setMuteOn(self):
        """Mute the room"""
        await self.director.sendPostRequest(
            "/api/v1/items/{}/commands".format(self.item_id),
            "MUTE_ON",
            {},
        )

    async def setMuteOff(self):
        """Unmute the room"""
        await self.director.sendPostRequest(
            "/api/v1/items/{}/commands".format(self.item_id),
            "MUTE_OFF",
            {},
        )

    async def toggleMute(self):
        """Toggle the current mute state for the room"""
        await self.director.sendPostRequest(
            "/api/v1/items/{}/commands".format(self.item_id),
            "MUTE_TOGGLE",
            {},
        )

    async def setVolume(self, volume: int):
        """Set the room volume, 0-100"""
        await self.director.sendPostRequest(
            "/api/v1/items/{}/commands".format(self.item_id),
            "SET_VOLUME_LEVEL",
            {"LEVEL": volume},
        )

    async def setIncrementVolume(self):
        """Decrease volume by 1"""
        await self.director.sendPostRequest(
            "/api/v1/items/{}/commands".format(self.item_id),
            "PULSE_VOL_UP",
            {},
        )

    async def setDecrementVolume(self):
        """Decrease volume by 1"""
        await self.director.sendPostRequest(
            "/api/v1/items/{}/commands".format(self.item_id),
            "PULSE_VOL_DOWN",
            {},
        )

    async def setPlay(self):
        await self.director.sendPostRequest(
            "/api/v1/items/{}/commands".format(self.item_id),
            "PLAY",
            {},
        )

    async def setPause(self):
        await self.director.sendPostRequest(
            "/api/v1/items/{}/commands".format(self.item_id),
            "PAUSE",
            {},
        )

    async def setStop(self):
        """Stops the currently playing media but does not turn off the room"""
        await self.director.sendPostRequest(
            "/api/v1/items/{}/commands".format(self.item_id),
            "STOP",
            {},
        )

    async def getAudioDevices(self):
        """
        Note: As tested in OS 3.2.3 this doesn't work, but may work in previous versions

        Get the audio devices located in the room.
        Note that this is literally the devices in the room,
        not necessarily all devices _playable_ in the room.
        See C4Director.getUiConfiguration for a more accurate list
        """
        await self.director.sendGetRequest(
            "/api/v1/locations/rooms/{}/audio_devices".format(self.item_id)
        )

    async def getVideoDevices(self):
        """
        Note: As tested in OS 3.2.3 this doesn't work, but may work in previous versions

        Get the video devices located in the room.
        Note that this is literally the devices in the room,
        not necessarily all devices _playable_ in the room.
        See C4Director.getUiConfiguration for a more accurate list
        """
        await self.director.sendGetRequest(
            "/api/v1/locations/rooms/{}/video_devices".format(self.item_id)
        )
