"""Controls Control4 security panel, security zones, and contact sensor
(door, window, motion) devices.
"""

from __future__ import annotations

import json
from enum import IntEnum

from pyControl4 import C4Entity
from pyControl4.director import C4Director


class C4ZoneType(IntEnum):
    """Control4 security zone types.

    These correspond to the type_id values returned by GET_ZONE_LIST.
    """

    UNKNOWN = 0
    CONTACT_SENSOR = 1
    EXTERIOR_DOOR = 2
    EXTERIOR_WINDOW = 3
    INTERIOR_DOOR = 4
    MOTION_SENSOR = 5
    FIRE = 6
    GAS = 7
    CO = 8
    HEAT = 9
    WATER = 10
    SMOKE = 11
    PRESSURE = 12
    GLASS_BREAK = 13
    GATE = 14
    GARAGE = 15
    COLD = 16

    @classmethod
    def get_name(cls, type_id: int) -> str:
        """Get human-readable name for a zone type ID."""
        names = {
            cls.UNKNOWN: "Unknown",
            cls.CONTACT_SENSOR: "Contact Sensor",
            cls.EXTERIOR_DOOR: "Exterior Door",
            cls.EXTERIOR_WINDOW: "Exterior Window",
            cls.INTERIOR_DOOR: "Interior Door",
            cls.MOTION_SENSOR: "Motion Sensor",
            cls.FIRE: "Fire Sensor",
            cls.GAS: "Gas Detector",
            cls.CO: "CO Detector",
            cls.HEAT: "Heat Detector",
            cls.WATER: "Water Sensor",
            cls.SMOKE: "Smoke Detector",
            cls.PRESSURE: "Pressure Sensor",
            cls.GLASS_BREAK: "Glass Break Sensor",
            cls.GATE: "Gate Sensor",
            cls.GARAGE: "Garage Door Sensor",
            cls.COLD: "Cold Sensor",
        }
        return names.get(type_id, "Security Zone")


class C4SecurityPanel(C4Entity):
    async def get_arm_state(self) -> str | None:
        """
        NOTE: Prefer using `get_partition_state()`
        and `get_armed_type()` over this method.
        Returns the arm state of the security panel as "DISARMED", "ARMED_HOME",
        or "ARMED_AWAY".
        """
        disarmed = await self.director.get_item_variable_value(
            self.item_id, "DISARMED_STATE"
        )
        armed_home = await self.director.get_item_variable_value(
            self.item_id, "HOME_STATE"
        )
        armed_away = await self.director.get_item_variable_value(
            self.item_id, "AWAY_STATE"
        )
        try:
            if disarmed is not None and int(disarmed) == 1:
                return "DISARMED"
            elif armed_home is not None and int(armed_home) == 1:
                return "ARMED_HOME"
            elif armed_away is not None and int(armed_away) == 1:
                return "ARMED_AWAY"
        except (ValueError, TypeError):
            pass
        return None

    async def get_alarm_state(self) -> bool | None:
        """Returns `True` if alarm is triggered, otherwise returns `False`."""
        alarm_state = await self.director.get_item_variable_value(
            self.item_id, "ALARM_STATE"
        )
        if alarm_state is None:
            return None
        return bool(alarm_state)

    async def get_display_text(self) -> str | None:
        """Returns the display text of the security panel."""
        display_text = await self.director.get_item_variable_value(
            self.item_id, "DISPLAY_TEXT"
        )
        return display_text

    async def get_trouble_text(self) -> str | None:
        """Returns the trouble display text of the security panel."""
        trouble_text = await self.director.get_item_variable_value(
            self.item_id, "TROUBLE_TEXT"
        )
        return trouble_text

    async def get_partition_state(self) -> str | None:
        """Returns the partition state of the security panel.

        Possible values include "DISARMED_NOT_READY", "DISARMED_READY", "ARMED_HOME",
        "ARMED_AWAY", "EXIT_DELAY", "ENTRY_DELAY"
        """
        partition_state = await self.director.get_item_variable_value(
            self.item_id, "PARTITION_STATE"
        )
        return partition_state

    async def get_delay_time_total(self) -> int | None:
        """Returns the total exit delay time. Returns 0 if an exit delay is not
        currently running.
        """
        delay_time_total = await self.director.get_item_variable_value(
            self.item_id, "DELAY_TIME_TOTAL"
        )
        return int(delay_time_total) if delay_time_total is not None else None

    async def get_delay_time_remaining(self) -> int | None:
        """Returns the remaining exit delay time. Returns 0 if an exit delay is
        not currently running.
        """
        delay_time_remaining = await self.director.get_item_variable_value(
            self.item_id, "DELAY_TIME_REMAINING"
        )
        return int(delay_time_remaining) if delay_time_remaining is not None else None

    async def get_open_zone_count(self) -> int | None:
        """Returns the number of open/unsecured zones."""
        open_zone_count = await self.director.get_item_variable_value(
            self.item_id, "OPEN_ZONE_COUNT"
        )
        return int(open_zone_count) if open_zone_count is not None else None

    async def get_alarm_type(self) -> str | None:
        """Returns details about the current alarm type."""
        alarm_type = await self.director.get_item_variable_value(
            self.item_id, "ALARM_TYPE"
        )
        return alarm_type

    async def get_armed_type(self) -> str | None:
        """Returns details about the current arm type."""
        armed_type = await self.director.get_item_variable_value(
            self.item_id, "ARMED_TYPE"
        )
        return armed_type

    async def get_last_emergency(self) -> str | None:
        """Returns details about the last emergency trigger."""
        last_emergency = await self.director.get_item_variable_value(
            self.item_id, "LAST_EMERGENCY"
        )
        return last_emergency

    async def get_last_arm_failure(self) -> str | None:
        """Returns details about the last arm failure."""
        last_arm_failed = await self.director.get_item_variable_value(
            self.item_id, "LAST_ARM_FAILED"
        )
        return last_arm_failed

    async def set_arm(self, usercode: str, mode: str) -> None:
        """Arms the security panel with the specified mode.

        Parameters:
            `usercode` - PIN/code for arming the system.

            `mode` - Arm mode to use. This depends on what is supported by the
                security panel itself.
        """
        usercode = str(usercode)
        await self.director.send_post_request(
            f"/api/v1/items/{self.item_id}/commands",
            "PARTITION_ARM",
            {"ArmType": mode, "UserCode": usercode},
        )

    async def set_disarm(self, usercode: str) -> None:
        """Disarms the security panel.

        Parameters:
            `usercode` - PIN/code for disarming the system.
        """
        usercode = str(usercode)
        await self.director.send_post_request(
            f"/api/v1/items/{self.item_id}/commands",
            "PARTITION_DISARM",
            {"UserCode": usercode},
        )

    async def get_emergency_types(self) -> list[str]:
        """Returns the available emergency types as a list.

        Possible types are "Fire", "Medical", "Panic", and "Police".
        """
        types_list: list[str] = []

        data = await self.director.get_item_info(self.item_id)
        if not data or not isinstance(data, list) or len(data) == 0:
            return types_list

        capabilities = data[0].get("capabilities", {})
        if capabilities.get("has_fire"):
            types_list.append("Fire")
        if capabilities.get("has_medical"):
            types_list.append("Medical")
        if capabilities.get("has_panic"):
            types_list.append("Panic")
        if capabilities.get("has_police"):
            types_list.append("Police")

        return types_list

    async def get_arm_types(self) -> list[str]:
        """Returns the available arm types as a list."""
        data = await self.director.get_item_info(self.item_id)
        if not data or not isinstance(data, list) or len(data) == 0:
            return []

        capabilities = data[0].get("capabilities", {})
        arm_types_str = capabilities.get("arm_types", "")
        if not arm_types_str:
            return []
        return [t.strip() for t in arm_types_str.split(",") if t.strip()]

    async def trigger_emergency(self, emergency_type: str) -> None:
        """Triggers an emergency of the specified type.

        Parameters:
            `emergency_type` - Type of emergency:
            "Fire", "Medical", "Panic", or "Police"
        """
        await self.director.send_post_request(
            f"/api/v1/items/{self.item_id}/commands",
            "EXECUTE_EMERGENCY",
            {"EmergencyType": emergency_type},
        )

    async def send_key_press(self, key: str) -> None:
        """Sends a single keypress to the security panel's virtual keypad (if
        supported).

        Parameters:
            `key` - Keypress to send. Only one key at a time.
        """
        key = str(key)
        await self.director.send_post_request(
            f"/api/v1/items/{self.item_id}/commands",
            "KEY_PRESS",
            {"KeyName": key},
        )

    async def get_zones(self) -> list[dict] | None:
        """Returns a list of all security zones for this partition.

        Each zone is a dictionary with the following keys:
            - `id` (int): Zone ID
            - `name` (str): Zone name
            - `room_id` (int): Room ID where the zone is located
            - `room_name` (str): Room name where the zone is located
            - `type_id` (int): Zone type ID (see C4ZoneType enum)
            - `is_open` (bool): True if zone is open/triggered
            - `is_bypassed` (bool): True if zone is bypassed
            - `is_chimeable` (bool): True if zone can chime
            - `can_bypass` (bool): True if zone can be bypassed
            - `can_control` (bool): True if zone can be controlled
        """
        result = await self.director.send_post_request(
            f"/api/v1/items/{self.item_id}/commands",
            "GET_ZONE_LIST",
            {},
            is_async=False,
        )
        if result:
            try:
                data = json.loads(result)
                zones = data.get("zones", {})
                # Handle both list and single zone response
                zone_list = zones.get("zone", [])
                if isinstance(zone_list, dict):
                    zone_list = [zone_list]
                return zone_list
            except (json.JSONDecodeError, AttributeError):
                return None
        return None

    async def get_open_zones(self) -> list[dict] | None:
        """Returns a list of only open (unsecured) zones for this partition.

        Returns the same zone structure as `get_zones()`, but filtered to only
        include zones that are currently open/triggered.
        """
        result = await self.director.send_post_request(
            f"/api/v1/items/{self.item_id}/commands",
            "GET_OPEN_ZONE_LIST",
            {},
            is_async=False,
        )
        if result:
            try:
                data = json.loads(result)
                zones = data.get("zones", {})
                zone_list = zones.get("zone", [])
                if isinstance(zone_list, dict):
                    zone_list = [zone_list]
                return zone_list
            except (json.JSONDecodeError, AttributeError):
                return None
        return None


class C4ContactSensor:
    def __init__(self, director: C4Director, item_id: int) -> None:
        """Creates a Control4 Contact Sensor object.

        Parameters:
            `director` - A `pyControl4.director.C4Director` object that corresponds
                to the Control4 Director that the contact sensor is connected to.

            `item_id` - The Control4 item ID of the contact sensor.
        """
        self.director = director
        self.item_id = item_id

    async def get_contact_state(self) -> bool | None:
        """Returns `True` if contact is triggered (door/window is closed, motion is
        detected), otherwise returns `False`.
        """
        contact_state = await self.director.get_item_variable_value(
            self.item_id, "ContactState"
        )
        if contact_state is None:
            return None
        return bool(contact_state)
