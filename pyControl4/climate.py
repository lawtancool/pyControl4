"""Controls Control4 Climate Control devices."""

from pyControl4 import C4Entity


class C4Climate(C4Entity):
    # ------------------------
    # HVAC and Fan States
    # ------------------------

    async def getHVACState(self):
        """Returns the current HVAC state (e.g., on/off or active mode)."""
        return await self.director.getItemVariableValue(self.item_id, "HVAC_STATE")

    async def getFANState(self):
        """Returns the current power state of the fan (True=on, False=off)."""
        return await self.director.getItemVariableValue(self.item_id, "FAN_STATE")

    # ------------------------
    # Mode Getters
    # ------------------------

    async def getHVACMode(self):
        """Returns the currently active HVAC mode."""
        return await self.director.getItemVariableValue(self.item_id, "HVAC_MODE")

    async def getHVACModes(self):
        """Returns a list of supported HVAC modes."""
        return await self.director.getItemVariableValue(self.item_id, "HVAC_MODES_LIST")

    async def getFANMode(self):
        """Returns the currently active fan mode."""
        return await self.director.getItemVariableValue(self.item_id, "FAN_MODE")

    async def getFANModes(self):
        """Returns a list of supported fan modes."""
        return await self.director.getItemVariableValue(self.item_id, "FAN_MODES_LIST")

    # ------------------------
    # Setpoint Getters
    # ------------------------

    async def getCoolSetpointF(self):
        """Returns the cooling setpoint temperature in Fahrenheit."""
        return await self.director.getItemVariableValue(self.item_id, "COOL_SETPOINT_F")

    async def getHeatSetpointF(self):
        """Returns the heating setpoint temperature in Fahrenheit."""
        return await self.director.getItemVariableValue(self.item_id, "HEAT_SETPOINT_F")

    # ------------------------
    # Sensor Readings
    # ------------------------

    async def getHumidity(self):
        """Returns the current humidity percentage."""
        return await self.director.getItemVariableValue(self.item_id, "HUMIDITY")

    async def getCurrentTemperature(self):
        """Returns the current ambient temperature in Fahrenheit."""
        return await self.director.getItemVariableValue(self.item_id, "TEMPERATURE_F")

    # ------------------------
    # Setters / Commands
    # ------------------------

    async def setTemperature(self, temp):
        """Sets the cooling setpoint temperature in Fahrenheit."""
        await self.setCoolSetpoint(temp)  # Delegates to the proper method

    async def setCoolSetpoint(self, temp):
        """Sets the cooling setpoint temperature in Fahrenheit."""
        await self.director.sendPostRequest(
            f"/api/v1/items/{self.item_id}/commands",
            "SET_SETPOINT_COOL",
            {"FAHRENHEIT": temp},
        )

    async def setHeatSetpoint(self, temp):
        """Sets the heating setpoint temperature in Fahrenheit."""
        await self.director.sendPostRequest(
            f"/api/v1/items/{self.item_id}/commands",
            "SET_SETPOINT_HEAT",
            {"FAHRENHEIT": temp},
        )

    async def setHvacMode(self, mode):
        """Sets the HVAC operating mode (e.g., heat, cool, auto)."""
        await self.director.sendPostRequest(
            f"/api/v1/items/{self.item_id}/commands",
            "SET_MODE_HVAC",
            {"MODE": mode},
        )

    async def setFanMode(self, mode):
        """Sets the fan operating mode (e.g., auto, on, circulate)."""
        await self.director.sendPostRequest(
            f"/api/v1/items/{self.item_id}/commands",
            "SET_MODE_FAN",
            {"MODE": mode},
        )

    async def setPreset(self, preset):
        """Applies a predefined climate preset by name."""
        await self.director.sendPostRequest(
            f"/api/v1/items/{self.item_id}/commands",
            "SET_PRESET",
            {"NAME": preset},
        )
