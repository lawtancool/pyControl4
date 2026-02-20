"""Controls Control4 security panel and contact sensor (door, window, motion)
devices.
"""

from pyControl4 import C4Entity


class C4SecurityPanel(C4Entity):
    async def get_arm_state(self) -> str | None:
        """Returns the arm state of the security panel as "DISARMED", "ARMED_HOME",
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
        if disarmed == 1:
            return "DISARMED"
        elif armed_home == 1:
            return "ARMED_HOME"
        elif armed_away == 1:
            return "ARMED_AWAY"
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

    async def trigger_emergency(self, type: str) -> None:
        """Triggers an emergency of the specified type.

        Parameters:
            `type` - Type of emergency: "Fire", "Medical", "Panic", or "Police"
        """
        await self.director.send_post_request(
            f"/api/v1/items/{self.item_id}/commands",
            "EXECUTE_EMERGENCY",
            {"EmergencyType": type},
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


class C4ContactSensor:
    def __init__(self, C4Director, item_id):
        """Creates a Control4 Contact Sensor object.

        Parameters:
            `C4Director` - A `pyControl4.director.C4Director` object that corresponds
                to the Control4 Director that the security panel is connected to.

            `item_id` - The Control4 item ID of the contact sensor.
        """
        self.director = C4Director
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
