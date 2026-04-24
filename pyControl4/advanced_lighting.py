"""Controls Control4 Advanced Lighting scenes."""

from __future__ import annotations

import json
from typing import Any

from pyControl4.director import C4Director

ADVANCED_LIGHTING_PATH = "/api/v1/agents/advanced_lighting"
ADVANCED_LIGHTING_COMMANDS_PATH = "/api/v1/agents/advanced_lighting/commands"


class C4AdvancedLighting:
    """Provides access to Control4 Advanced Lighting scenes.

    The Advanced Lighting agent manages named lighting scenes that can
    activate, deactivate, or toggle groups of lights simultaneously.

    Use ``C4AdvancedLighting.create(director)`` to construct an instance —
    it fetches the agent's internal device ID from the Director automatically.
    """

    def __init__(self, director: C4Director, agent_device_id: int) -> None:
        """Creates a C4AdvancedLighting object.

        Parameters:
            `director` - A `pyControl4.director.C4Director` object.

            `agent_device_id` - The Control4 item ID of the Advanced Lighting
                agent device. Obtain this via `C4AdvancedLighting.create()`.
        """
        self.director = director
        self.agent_device_id = int(agent_device_id)

    @classmethod
    async def create(cls, director: C4Director) -> C4AdvancedLighting:
        """Creates a C4AdvancedLighting instance by fetching the agent device
        ID from the Director.

        Parameters:
            `director` - A `pyControl4.director.C4Director` object.

        Raises:
            `ValueError` if the Advanced Lighting agent is not present or
            returns no commands.
        """
        data = await director.send_get_request(ADVANCED_LIGHTING_COMMANDS_PATH)
        commands: list[dict[str, Any]] = json.loads(data)
        if not commands:
            raise ValueError(
                "Advanced Lighting agent returned no commands — "
                "is the Advanced Lighting agent enabled in Control4?"
            )
        agent_device_id: int = commands[0]["deviceId"]
        return cls(director, agent_device_id)

    async def get_scenes(self) -> list[dict[str, Any]]:
        """Returns a list of Advanced Lighting scenes from the Director.

        Each scene dict contains:

        - ``scene_id`` (int): Unique scene identifier
        - ``name`` (str): Scene display name
        - ``is_active`` (bool): Whether the scene is currently active
        - ``ramp_capable`` (bool): Whether the scene supports ramping
        - ``full_on`` (bool): Whether the scene sets all loads to full on
        - ``full_off`` (bool): Whether the scene sets all loads to full off
        - ``user_defined`` (bool): Whether the scene was defined by a user
        - ``lock_loads`` (bool): Whether the scene locks loads from other changes
        """
        data = await self.director.send_get_request(ADVANCED_LIGHTING_PATH)
        result: list[dict[str, Any]] = json.loads(data)
        return result

    async def activate_scene(self, scene_id: int) -> None:
        """Activates a lighting scene.

        Parameters:
            `scene_id` - The Control4 scene ID (from ``get_scenes()``).
        """
        await self.director.send_post_request(
            f"/api/v1/items/{self.agent_device_id}/commands",
            "ACTIVATE_SCENE",
            {"SCENE_ID": scene_id},
        )

    async def deactivate_scene(self, scene_id: int) -> None:
        """Deactivates a lighting scene.

        Parameters:
            `scene_id` - The Control4 scene ID (from ``get_scenes()``).
        """
        await self.director.send_post_request(
            f"/api/v1/items/{self.agent_device_id}/commands",
            "DEACTIVATE_SCENE",
            {"SCENE_ID": scene_id},
        )

    async def toggle_scene(self, scene_id: int) -> None:
        """Toggles a lighting scene between active and inactive.

        Parameters:
            `scene_id` - The Control4 scene ID (from ``get_scenes()``).
        """
        await self.director.send_post_request(
            f"/api/v1/items/{self.agent_device_id}/commands",
            "TOGGLE_SCENE",
            {"SCENE_ID": scene_id},
        )
