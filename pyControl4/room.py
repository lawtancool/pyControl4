"""Controls Control4 Room devices."""

from __future__ import annotations

import json
from typing import Any

from pyControl4 import C4Entity


class C4Room(C4Entity):
    """
    A media-oriented view of a Control4 Room, supporting items of type="room"
    """

    async def is_room_hidden(self) -> bool | None:
        """Returns True if the room is hidden from the end-user"""
        value = await self.director.get_item_variable_value(self.item_id, "ROOM_HIDDEN")
        if value is None:
            return None
        return int(value) != 0

    async def is_on(self) -> bool | None:
        """Returns True/False if the room is "ON" from the director's perspective"""
        value = await self.director.get_item_variable_value(self.item_id, "POWER_STATE")
        if value is None:
            return None
        return int(value) != 0

    async def set_room_off(self) -> None:
        """Turn the room "OFF" """
        await self.director.send_post_request(
            f"/api/v1/items/{self.item_id}/commands",
            "ROOM_OFF",
            {},
        )

    async def _set_source(self, source_id: int, audio_only: bool) -> None:
        """
        Sets the room source, turning on the room if necessary.
        If audio_only, only the current audio device is changed
        """
        await self.director.send_post_request(
            f"/api/v1/items/{self.item_id}/commands",
            "SELECT_AUDIO_DEVICE" if audio_only else "SELECT_VIDEO_DEVICE",
            {"deviceid": source_id},
        )

    async def set_audio_source(self, source_id: int) -> None:
        """Sets the current audio source for the room"""
        await self._set_source(source_id, audio_only=True)

    async def set_video_and_audio_source(self, source_id: int) -> None:
        """Sets the current audio and video source for the room"""
        await self._set_source(source_id, audio_only=False)

    async def get_volume(self) -> int | None:
        """Returns the current volume for the room from 0-100"""
        value = await self.director.get_item_variable_value(
            self.item_id, "CURRENT_VOLUME"
        )
        if value is None:
            return None
        return int(value)

    async def is_muted(self) -> bool | None:
        """Returns True if the room is muted"""
        value = await self.director.get_item_variable_value(self.item_id, "IS_MUTED")
        if value is None:
            return None
        return int(value) != 0

    async def set_mute_on(self) -> None:
        """Mute the room"""
        await self.director.send_post_request(
            f"/api/v1/items/{self.item_id}/commands",
            "MUTE_ON",
            {},
        )

    async def set_mute_off(self) -> None:
        """Unmute the room"""
        await self.director.send_post_request(
            f"/api/v1/items/{self.item_id}/commands",
            "MUTE_OFF",
            {},
        )

    async def toggle_mute(self) -> None:
        """Toggle the current mute state for the room"""
        await self.director.send_post_request(
            f"/api/v1/items/{self.item_id}/commands",
            "MUTE_TOGGLE",
            {},
        )

    async def set_volume(self, volume: int) -> None:
        """Set the room volume, 0-100"""
        await self.director.send_post_request(
            f"/api/v1/items/{self.item_id}/commands",
            "SET_VOLUME_LEVEL",
            {"LEVEL": volume},
        )

    async def set_increment_volume(self) -> None:
        """Increase volume by 1"""
        await self.director.send_post_request(
            f"/api/v1/items/{self.item_id}/commands",
            "PULSE_VOL_UP",
            {},
        )

    async def set_decrement_volume(self) -> None:
        """Decrease volume by 1"""
        await self.director.send_post_request(
            f"/api/v1/items/{self.item_id}/commands",
            "PULSE_VOL_DOWN",
            {},
        )

    async def set_play(self) -> None:
        await self.director.send_post_request(
            f"/api/v1/items/{self.item_id}/commands",
            "PLAY",
            {},
        )

    async def set_pause(self) -> None:
        await self.director.send_post_request(
            f"/api/v1/items/{self.item_id}/commands",
            "PAUSE",
            {},
        )

    async def set_stop(self) -> None:
        """Stops the currently playing media but does not turn off the room"""
        await self.director.send_post_request(
            f"/api/v1/items/{self.item_id}/commands",
            "STOP",
            {},
        )

    async def get_audio_devices(self) -> dict[str, Any]:
        """
        Note: As tested in OS 3.2.3 this doesn't work, but may work in previous versions

        Get the audio devices located in the room.
        Note that this is literally the devices in the room,
        not necessarily all devices _playable_ in the room.
        See `pyControl4.director.C4Director.get_ui_configuration`
        for a more accurate list
        """
        data = await self.director.send_get_request(
            f"/api/v1/locations/rooms/{self.item_id}/audio_devices"
        )
        result: dict[str, Any] = json.loads(data)
        return result

    async def get_video_devices(self) -> dict[str, Any]:
        """
        Note: As tested in OS 3.2.3 this doesn't work, but may work in previous versions

        Get the video devices located in the room.
        Note that this is literally the devices in the room,
        not necessarily all devices _playable_ in the room.
        See `pyControl4.director.C4Director.get_ui_configuration`
        for a more accurate list
        """
        data = await self.director.send_get_request(
            f"/api/v1/locations/rooms/{self.item_id}/video_devices"
        )
        result: dict[str, Any] = json.loads(data)
        return result
