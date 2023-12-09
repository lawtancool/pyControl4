"""Controls Control4 Light devices.
"""


from pyControl4 import C4Entity


class C4Climate(C4Entity):
    async def getHVACState(self):
        """Returns the power state of thee fan as a boolean (True=on, False=off)."""
        value = await self.director.getItemVariableValue(self.item_id, "HVAC_STATE")
        return value

    async def getHVACModes(self):
        """Returns the power state of thee fan as a boolean (True=on, False=off)."""
        value = await self.director.getItemVariableValue(
            self.item_id, "HVAC_MODES_LIST"
        )
        return value

    async def getHVACMode(self):
        """Returns the power state of thee fan as a boolean (True=on, False=off)."""
        value = await self.director.getItemVariableValue(self.item_id, "HVAC_MODE")
        return value

    async def getFANModes(self):
        """Returns the power state of thee fan as a boolean (True=on, False=off)."""
        value = await self.director.getItemVariableValue(self.item_id, "FAN_MODES_LIST")
        return value

    async def getFANMode(self):
        """Returns the power state of thee fan as a boolean (True=on, False=off)."""
        value = await self.director.getItemVariableValue(self.item_id, "FAN_MODE")
        return value

    async def getFANState(self):
        """Returns the power state of thee fan as a boolean (True=on, False=off)."""
        value = await self.director.getItemVariableValue(self.item_id, "FAN_STATE")
        return value

    async def getCoolSetpointF(self):
        """Returns the power state of thee fan as a boolean (True=on, False=off)."""
        value = await self.director.getItemVariableValue(
            self.item_id, "COOL_SETPOINT_F"
        )
        return value

    async def getHeatSetpointF(self):
        """Returns the power state of thee fan as a boolean (True=on, False=off)."""
        value = await self.director.getItemVariableValue(
            self.item_id, "HEAT_SETPOINT_F"
        )
        return value

    async def getHumidity(self):
        """Returns the power state of thee fan as a boolean (True=on, False=off)."""
        value = await self.director.getItemVariableValue(self.item_id, "HUMIDITY")
        return value

    async def getCurrentTemperature(self):
        """Returns the power state of thee fan as a boolean (True=on, False=off)."""
        value = await self.director.getItemVariableValue(self.item_id, "TEMPERATURE_F")
        return value

    async def setTemperature(self, temp):
        await self.director.sendPostRequest(
            "/api/v1/items/{}/commands".format(self.item_id),
            "SET_SETPOINT_COOL",
            {"FAHRENHEIT": temp},
        )

    async def setCoolSetpoint(self, temp):
        await self.director.sendPostRequest(
            "/api/v1/items/{}/commands".format(self.item_id),
            "SET_SETPOINT_COOL",
            {"FAHRENHEIT": temp},
        )

    async def setHeatSetpoint(self, temp):
        await self.director.sendPostRequest(
            "/api/v1/items/{}/commands".format(self.item_id),
            "SET_SETPOINT_HEAT",
            {"FAHRENHEIT": temp},
        )

    async def setHvacMode(self, mode):
        await self.director.sendPostRequest(
            "/api/v1/items/{}/commands".format(self.item_id),
            "SET_MODE_HVAC",
            {"MODE": mode},
        )

    async def setFanMode(self, mode):
        await self.director.sendPostRequest(
            "/api/v1/items/{}/commands".format(self.item_id),
            "SET_MODE_FAN",
            {"MODE": mode},
        )

    async def setPreset(self, preset):
        await self.director.sendPostRequest(
            "/api/v1/items/{}/commands".format(self.item_id),
            "SET_PRESET",
            {"NAME": preset},
        )
