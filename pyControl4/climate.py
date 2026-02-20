"""Controls Control4 Climate Control devices."""

from __future__ import annotations

from pyControl4 import C4Entity


class C4Climate(C4Entity):
    # ------------------------
    # HVAC and Fan States
    # ------------------------

    async def get_hvac_state(self) -> str | None:
        """Returns the current HVAC state (e.g., on/off or active mode)."""
        return await self.director.get_item_variable_value(self.item_id, "HVAC_STATE")

    async def get_fan_state(self) -> str | None:
        """Returns the current power state of the fan (on, off)."""
        return await self.director.get_item_variable_value(self.item_id, "FAN_STATE")

    # ------------------------
    # Mode Getters
    # ------------------------

    async def get_hvac_mode(self) -> str | None:
        """Returns the currently active HVAC mode."""
        return await self.director.get_item_variable_value(self.item_id, "HVAC_MODE")

    async def get_hvac_modes(self) -> str | None:
        """Returns a list of supported HVAC modes."""
        return await self.director.get_item_variable_value(
            self.item_id, "HVAC_MODES_LIST"
        )

    async def get_fan_mode(self) -> str | None:
        """Returns the currently active fan mode."""
        return await self.director.get_item_variable_value(self.item_id, "FAN_MODE")

    async def get_fan_modes(self) -> str | None:
        """Returns a list of supported fan modes."""
        return await self.director.get_item_variable_value(
            self.item_id, "FAN_MODES_LIST"
        )

    async def get_hold_mode(self) -> str | None:
        """Returns the currently active hold mode."""
        return await self.director.get_item_variable_value(self.item_id, "HOLD_MODE")

    async def get_hold_modes(self) -> str | None:
        """Returns a list of supported hold modes."""
        return await self.director.get_item_variable_value(
            self.item_id, "HOLD_MODES_LIST"
        )

    # ------------------------
    # Setpoint Getters
    # ------------------------

    async def get_cool_setpoint_f(self) -> float | None:
        """Returns the cooling setpoint temperature in Fahrenheit."""
        value = await self.director.get_item_variable_value(
            self.item_id, "COOL_SETPOINT_F"
        )
        if value is None:
            return None
        return float(value)

    async def get_cool_setpoint_c(self) -> float | None:
        """Returns the cooling setpoint temperature in Celsius."""
        value = await self.director.get_item_variable_value(
            self.item_id, "COOL_SETPOINT_C"
        )
        if value is None:
            return None
        return float(value)

    async def get_heat_setpoint_f(self) -> float | None:
        """Returns the heating setpoint temperature in Fahrenheit."""
        value = await self.director.get_item_variable_value(
            self.item_id, "HEAT_SETPOINT_F"
        )
        if value is None:
            return None
        return float(value)

    async def get_heat_setpoint_c(self) -> float | None:
        """Returns the heating setpoint temperature in Celsius."""
        value = await self.director.get_item_variable_value(
            self.item_id, "HEAT_SETPOINT_C"
        )
        if value is None:
            return None
        return float(value)

    # ------------------------
    # Sensor Readings
    # ------------------------

    async def get_humidity(self) -> float | None:
        """Returns the current humidity percentage."""
        value = await self.director.get_item_variable_value(self.item_id, "HUMIDITY")
        if value is None:
            return None
        return float(value)

    async def get_current_temperature_f(self) -> float | None:
        """Returns the current ambient temperature in Fahrenheit."""
        value = await self.director.get_item_variable_value(
            self.item_id, "TEMPERATURE_F"
        )
        if value is None:
            return None
        return float(value)

    async def get_current_temperature_c(self) -> float | None:
        """Returns the current ambient temperature in Celsius."""
        value = await self.director.get_item_variable_value(
            self.item_id, "TEMPERATURE_C"
        )
        if value is None:
            return None
        return float(value)

    # ------------------------
    # Setters / Commands
    # ------------------------

    async def set_cool_setpoint_f(self, temp: float) -> None:
        """Sets the cooling setpoint temperature in Fahrenheit."""
        await self.director.send_post_request(
            f"/api/v1/items/{self.item_id}/commands",
            "SET_SETPOINT_COOL",
            {"FAHRENHEIT": temp},
        )

    async def set_cool_setpoint_c(self, temp: float) -> None:
        """Sets the cooling setpoint temperature in Celsius."""
        await self.director.send_post_request(
            f"/api/v1/items/{self.item_id}/commands",
            "SET_SETPOINT_COOL",
            {"CELSIUS": temp},
        )

    async def set_heat_setpoint_f(self, temp: float) -> None:
        """Sets the heating setpoint temperature in Fahrenheit."""
        await self.director.send_post_request(
            f"/api/v1/items/{self.item_id}/commands",
            "SET_SETPOINT_HEAT",
            {"FAHRENHEIT": temp},
        )

    async def set_heat_setpoint_c(self, temp: float) -> None:
        """Sets the heating setpoint temperature in Celsius."""
        await self.director.send_post_request(
            f"/api/v1/items/{self.item_id}/commands",
            "SET_SETPOINT_HEAT",
            {"CELSIUS": temp},
        )

    async def set_hvac_mode(self, mode: str) -> None:
        """Sets the HVAC operating mode (e.g., heat, cool, auto)."""
        await self.director.send_post_request(
            f"/api/v1/items/{self.item_id}/commands",
            "SET_MODE_HVAC",
            {"MODE": mode},
        )

    async def set_fan_mode(self, mode: str) -> None:
        """Sets the fan operating mode (e.g., auto, on, circulate)."""
        await self.director.send_post_request(
            f"/api/v1/items/{self.item_id}/commands",
            "SET_MODE_FAN",
            {"MODE": mode},
        )

    async def set_preset(self, preset: str) -> None:
        """Applies a predefined climate preset by name."""
        await self.director.send_post_request(
            f"/api/v1/items/{self.item_id}/commands",
            "SET_PRESET",
            {"NAME": preset},
        )

    async def set_hold_mode(self, mode: str) -> None:
        """Sets the hold mode."""
        await self.director.send_post_request(
            f"/api/v1/items/{self.item_id}/commands",
            "SET_MODE_HOLD",
            {"MODE": mode},
        )
