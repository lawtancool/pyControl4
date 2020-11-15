"""Controls Control4 security panel and contact sensor (door, window, motion) devices.
"""
import json


class C4SecurityPanel:
    def __init__(self, C4Director, item_id):
        """Creates a Control4 Security Panel object.

        Parameters:
            `C4Director` - A `pyControl4.director.C4Director` object that corresponds to the Control4 Director that the security panel is connected to.

            `item_id` - The Control4 item ID of the security panel partition.
        """
        self.director = C4Director
        self.item_id = item_id

    async def getArmState(self):
        """Returns the arm state of the security panel as "DISARMED", "ARMED_HOME", or "ARMED_AWAY"."""
        disarmed = await self.director.getItemVariableValue(
            self.item_id, "DISARMED_STATE"
        )
        armed_home = await self.director.getItemVariableValue(
            self.item_id, "HOME_STATE"
        )
        armed_away = await self.director.getItemVariableValue(
            self.item_id, "AWAY_STATE"
        )
        if disarmed == 1:
            return "DISARMED"
        elif armed_home == 1:
            return "ARMED_HOME"
        elif armed_away == 1:
            return "ARMED_AWAY"

    async def getAlarmState(self):
        """Returns `True` if alarm is triggered, otherwise returns `False`."""
        alarm_state = await self.director.getItemVariableValue(
            self.item_id, "ALARM_STATE"
        )
        return bool(alarm_state)

    async def getDisplayText(self):
        """Returns the display text of the security panel."""
        display_text = await self.director.getItemVariableValue(
            self.item_id, "DISPLAY_TEXT"
        )
        return display_text

    async def getTroubleText(self):
        """Returns the trouble display text of the security panel."""
        trouble_text = await self.director.getItemVariableValue(
            self.item_id, "TROUBLE_TEXT"
        )
        return trouble_text

    async def getPartitionState(self):
        """Returns the partition state of the security panel.

        Possible values include "DISARMED_NOT_READY", "DISARMED_READY", "ARMED_HOME", "ARMED_AWAY", "EXIT_DELAY", "ENTRY_DELAY"
        """
        partition_state = await self.director.getItemVariableValue(
            self.item_id, "PARTITION_STATE"
        )
        return partition_state

    async def getDelayTimeTotal(self):
        """Returns the total exit delay time. Returns 0 if an exit delay is not currently running."""
        delay_time_total = await self.director.getItemVariableValue(
            self.item_id, "DELAY_TIME_TOTAL"
        )
        return delay_time_total

    async def getDelayTimeRemaining(self):
        """Returns the remaining exit delay time. Returns 0 if an exit delay is not currently running."""
        delay_time_remaining = await self.director.getItemVariableValue(
            self.item_id, "DELAY_TIME_REMAINING"
        )
        return delay_time_remaining

    async def getOpenZoneCount(self):
        """Returns the number of open/unsecured zones."""
        open_zone_count = await self.director.getItemVariableValue(
            self.item_id, "OPEN_ZONE_COUNT"
        )
        return open_zone_count

    async def getAlarmType(self):
        """Returns details about the current alarm type."""
        alarm_type = await self.director.getItemVariableValue(
            self.item_id, "ALARM_TYPE"
        )
        return alarm_type

    async def getArmedType(self):
        """Returns details about the current arm type."""
        armed_type = await self.director.getItemVariableValue(
            self.item_id, "ARMED_TYPE"
        )
        return armed_type

    async def getLastEmergency(self):
        """Returns details about the last emergency trigger."""
        last_emergency = await self.director.getItemVariableValue(
            self.item_id, "LAST_EMERGENCY"
        )
        return last_emergency

    async def getLastArmFailure(self):
        """Returns details about the last arm failure."""
        last_arm_failed = await self.director.getItemVariableValue(
            self.item_id, "LAST_ARM_FAILED"
        )
        return last_arm_failed

    async def setArm(self, usercode, mode: str):
        """Arms the security panel with the specified mode.

        Parameters:
            `usercode` - PIN/code for arming the system.

            `mode` - Arm mode to use. This depends on what is supported by the security panel itself.
        """
        usercode = str(usercode)
        await self.director.sendPostRequest(
            "/api/v1/items/{}/commands".format(self.item_id),
            "PARTITION_ARM",
            {"ArmType": mode, "UserCode": usercode},
        )

    async def setDisarm(self, usercode):
        """Disarms the security panel.

        Parameters:
            `usercode` - PIN/code for disarming the system.
        """
        usercode = str(usercode)
        await self.director.sendPostRequest(
            "/api/v1/items/{}/commands".format(self.item_id),
            "PARTITION_DISARM",
            {"UserCode": usercode},
        )

    async def getEmergencyTypes(self):
        """Returns the available emergency types as a list.

        Possible types are "Fire", "Medical", "Panic", and "Police".
        """
        types_list = []

        data = await self.director.getItemInfo(self.item_id)
        jsonDictionary = json.loads(data)

        if jsonDictionary[0]["capabilities"]["has_fire"]:
            types_list.append("Fire")
        if jsonDictionary[0]["capabilities"]["has_medical"]:
            types_list.append("Medical")
        if jsonDictionary[0]["capabilities"]["has_panic"]:
            types_list.append("Panic")
        if jsonDictionary[0]["capabilities"]["has_police"]:
            types_list.append("Police")

        return types_list

    async def triggerEmergency(self, usercode, type):
        """Triggers an emergency of the specified type.

        Parameters:
            `usercode` - PIN/code for disarming the system.

            `type` - Type of emergency: "Fire", "Medical", "Panic", or "Police"
        """
        usercode = str(usercode)
        await self.director.sendPostRequest(
            "/api/v1/items/{}/commands".format(self.item_id),
            "PARTITION_DISARM",
            {"UserCode": usercode},
        )

    async def sendKeyPress(self, key):
        """Sends a single keypress to the security panel's virtual keypad (if supported).

        Parameters:
            `key` - Keypress to send. Only one key at a time.
        """
        key = str(key)
        await self.director.sendPostRequest(
            "/api/v1/items/{}/commands".format(self.item_id),
            "KEY_PRESS",
            {"KeyName": key},
        )


class C4ContactSensor:
    def __init__(self, C4Director, item_id):
        """Creates a Control4 Contact Sensor object.

        Parameters:
            `C4Director` - A `pyControl4.director.C4Director` object that corresponds to the Control4 Director that the security panel is connected to.

            `item_id` - The Control4 item ID of the contact sensor.
        """
        self.director = C4Director
        self.item_id = item_id

    async def getContactState(self):
        """Returns `True` if contact is triggered (door/window is closed, motion is detected), otherwise returns `False`."""
        contact_state = await self.director.getItemVariableValue(
            self.item_id, "ContactState"
        )
        return bool(contact_state)
