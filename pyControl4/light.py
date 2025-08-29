"""Controls Control4 Light devices."""

from pyControl4 import C4Entity


class C4Light(C4Entity):
    async def getLevel(self):
        """Returns the level of a dimming-capable light as an int 0-100.
        Will cause an error if called on a non-dimmer switch. Use `getState()` instead.
        """
        value = await self.director.getItemVariableValue(self.item_id, "LIGHT_LEVEL")
        return int(value)

    async def getState(self):
        """Returns the power state of a dimmer or switch as a boolean (True=on, False=off)."""
        value = await self.director.getItemVariableValue(self.item_id, "LIGHT_STATE")
        return bool(value)

    async def setLevel(self, level):
        """Sets the light level of a dimmer or turns on/off a switch.
        Any `level > 0` will turn on a switch, and `level = 0` will turn off a switch.

        Parameters:
            `level` - (int) 0-100
        """
        await self.director.sendPostRequest(
            "/api/v1/items/{}/commands".format(self.item_id),
            "SET_LEVEL",
            {"LEVEL": level},
        )

    async def rampToLevel(self, level, time):
        """Ramps the light level of a dimmer over time.
        Any `level > 0` will turn on a switch, and `level = 0` will turn off a switch.

        Parameters:
            `level` - (int) 0-100

            `time` - (int) Duration in milliseconds
        """
        await self.director.sendPostRequest(
            "/api/v1/items/{}/commands".format(self.item_id),
            "RAMP_TO_LEVEL",
            {"LEVEL": level, "TIME": time},
        )

    async def setColorXY(self, x: float, y: float, *, rate: int | None = None, mode: int = 0):
        """
        Sends SET_COLOR_TARGET with xy and mode.
        - x, y: CIE 1931 coordinates (0..1 ~ typically)
        - rate: ramp duration in milliseconds (Optional)
        - mode: 0 = full color, 1 = CCT
        """
        params = {
            "LIGHT_COLOR_TARGET_X": float(x),
            "LIGHT_COLOR_TARGET_Y": float(y),
            "LIGHT_COLOR_TARGET_MODE": int(mode),
        }
        if rate is not None:
            params["RATE"] = int(rate)

        await self.director.sendPostRequest(
            f"/api/v1/items/{self.item_id}/commands",
            "SET_COLOR_TARGET",
            params,
        )

    async def setColorRGB(self, r: int, g: int, b: int, *, rate: int | None = None):
        """RGB 0..255 -> xy, mode=0 (full color)."""
        x, y = self._rgb_to_xy(r, g, b)
        await self.setColorXY(x, y, rate=rate, mode=0)

    async def setColorHex(self, hex_color: str, *, rate: int | None = None):
        """HEX (#RRGGBB/#RGB/RRGGBB/RGB) -> xy, mode=0 (full color)."""
        r, g, b = self._hex_to_rgb(hex_color)
        await self.setColorRGB(r, g, b, rate=rate)

    async def setColorTemperature(self, kelvin: int, *, rate: int | None = None):
        """Kelvin -> xy, mode=1 (CCT)."""
        x, y = self._cct_to_xy(kelvin)
        await self.setColorXY(x, y, rate=rate, mode=1)

# ---------- Color Utilities ----------
    @staticmethod
    def _hex_to_rgb(color: str) -> tuple[int, int, int]:
        s = color.strip()
        if s.startswith("#"):
            s = s[1:]
        if len(s) == 3:
            s = "".join(c * 2 for c in s)
        if len(s) != 6:
            raise ValueError("HEX color must be RRGGBB, #RRGGBB, #RGB or RGB")
        r = int(s[0:2], 16)
        g = int(s[2:4], 16)
        b = int(s[4:6], 16)
        return r, g, b

    @staticmethod
    def _srgb_to_linear(c: float) -> float:
        # c in [0..1]
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    @classmethod
    def _rgb_to_xy(cls, r: int, g: int, b: int) -> tuple[float, float]:
        # Normalize 0..255 -> 0..1 sRGB
        rs = r / 255.0
        gs = g / 255.0
        bs = b / 255.0
        # Correction gamma sRGB -> lin
        rlin = cls._srgb_to_linear(rs)
        glin = cls._srgb_to_linear(gs)
        blin = cls._srgb_to_linear(bs)
        # lin RGB -> XYZ (D65)
        X = rlin * 0.4124 + glin * 0.3576 + blin * 0.1805
        Y = rlin * 0.2126 + glin * 0.7152 + blin * 0.0722
        Z = rlin * 0.0193 + glin * 0.1192 + blin * 0.9505
        denom = X + Y + Z
        if denom <= 1e-9:
            return 0.3127, 0.3290  # fallback D65 if complete black
        x = X / denom
        y = Y / denom
        # Optionally round to 4 decimal places (many drivers prefer this)
        return round(x, 4), round(y, 4)

    @staticmethod
    def _cct_to_xy(kelvin: int) -> tuple[float, float]:
        """Approximation CIE 1931 xy for 1667K..25000K (classic formulas)."""
        K = float(kelvin)
        if K < 1667: K = 1667.0
        if K > 25000: K = 25000.0

        # x as a function of K
        if 1667 <= K <= 4000:
            x = (-0.2661239 * 1e9) / (K ** 3) - (0.2343580 * 1e6) / (K ** 2) + (0.8776956 * 1e3) / K + 0.179910
        else:  # 4000..25000
            x = (-3.0258469 * 1e9) / (K ** 3) + (2.1070379 * 1e6) / (K ** 2) + (0.2226347 * 1e3) / K + 0.240390

        # y as a function of x and K
        if 1667 <= K <= 2222:
            y = -1.1063814 * x**3 - 1.34811020 * x**2 + 2.18555832 * x - 0.20219683
        elif 2222 < K <= 4000:
            y = -0.9549476 * x**3 - 1.37418593 * x**2 + 2.09137015 * x - 0.16748867
        else:  # 4000..25000
            y = 3.0817580 * x**3 - 5.87338670 * x**2 + 3.75112997 * x - 0.37001483

        return round(x, 4), round(y, 4)

    