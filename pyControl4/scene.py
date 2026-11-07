"""Controls Control4 Advanced Lighting Scenes."""

from __future__ import annotations

import json
from typing import Any

from pyControl4.director import C4Director
from pyControl4.error_handling import NotFound

ADVANCED_LIGHTING_PROXY = "control4_agent_adv_lighting"
ADVANCED_LIGHTING_URI = "/api/v1/agents/advanced_lighting"

TOGGLE_NAME_SUFFIX = " (Toggle)"


async def find_advanced_lighting_agent(director: C4Director) -> int | None:
    """Returns the item id of the system's Advanced Lighting agent.

    The agent's item id differs between systems, so it has to be found by its
    proxy rather than hardcoded. Returns `None` on a system that has no
    Advanced Lighting agent, and therefore no scenes.

    Parameters:
        `director` - A `pyControl4.director.C4Director` object that corresponds
                     to the Control4 Director to search.
    """
    for item in await director.get_all_item_info():
        if item.get("proxy") == ADVANCED_LIGHTING_PROXY:
            item_id: int = item["id"]
            return item_id
    return None


def _toggle_companion_ids(scenes: list[dict[str, Any]]) -> set[int]:
    """Returns the `scene_id`s of scenes that are `(Toggle)` companions.

    A scene created in Composer Pro is accompanied by a generated companion
    scene, so the scene can be bound to a keypad button that flips it. The
    companion is named `<name> (Toggle)` and sits at the base scene's
    `scene_id` + 1. It reports the same `is_active` as the scene it toggles, so
    to a consumer listing scenes it is a duplicate.

    Both halves of the pattern have to line up -- the name suffix and the
    adjacent id -- before a scene is called a companion. A scene a user named
    "Movie (Toggle)" themselves is left alone, and so is a companion whose base
    scene the agent did not report. Erring this way leaves an extra scene in
    the list rather than hiding a real one.
    """
    ids_by_name: dict[str, set[int]] = {}
    for scene in scenes:
        ids_by_name.setdefault(scene["name"], set()).add(scene["scene_id"])

    return {
        scene["scene_id"]
        for scene in scenes
        if scene["name"].endswith(TOGGLE_NAME_SUFFIX)
        and scene["scene_id"] - 1
        in ids_by_name.get(scene["name"][: -len(TOGGLE_NAME_SUFFIX)], ())
    }


class C4AdvancedLighting:
    """The Advanced Lighting agent, which owns a system's lighting scenes.

    Scenes are not Director items, so they do not appear in
    `C4Director.get_all_item_info()`; they are listed from a fixed agent
    endpoint instead. Scene commands go to the agent's own item, whose id
    differs between systems and is looked up when it is first needed.

    This is deliberately not a `pyControl4.C4Entity`: an item id is not needed
    to construct one, and the agent is not a device.
    """

    def __init__(self, director: C4Director, item_id: int | None = None) -> None:
        """Creates the Advanced Lighting agent object.

        Parameters:
            `director` - A `pyControl4.director.C4Director` object that
                         corresponds to the Control4 Director that the agent
                         is on.

            `item_id` - The agent's Control4 item ID. Optional: when it is
                        not given, it is looked up once, the first time a
                        scene command is sent, and `item_id` is `None` until
                        then.
        """
        self.director = director
        self.item_id: int | None = None if item_id is None else int(item_id)

    async def _get_item_id(self) -> int:
        """Returns the agent's item id, looking it up once if it is not known.

        Raises `pyControl4.error_handling.NotFound` if the system has no
        Advanced Lighting agent, since there is then nothing to command.
        """
        if self.item_id is None:
            item_id = await find_advanced_lighting_agent(self.director)
            if item_id is None:
                raise NotFound(
                    "This Control4 system has no Advanced Lighting agent, "
                    "so it has no lighting scenes."
                )
            self.item_id = item_id
        return self.item_id

    async def get_scenes(
        self, *, include_toggle_companions: bool = False
    ) -> list[dict[str, Any]]:
        """Returns a list of the system's Advanced Lighting Scenes.

        Each scene has at least the keys `scene_id` (int), `name` (str) and
        `is_active` (bool). Systems may also report `ramp_capable`, `full_on`,
        `full_off`, `user_defined` and `lock_loads`.

        Generated `<name> (Toggle)` companion scenes are left out, since they
        duplicate the state of the scene they toggle.

        Parameters:
            `include_toggle_companions` - (bool) Return every scene the agent
                                          reports, companions included
        """
        data = await self.director.send_get_request(ADVANCED_LIGHTING_URI)
        scenes: list[dict[str, Any]] = json.loads(data)
        if include_toggle_companions:
            return scenes
        companion_ids = _toggle_companion_ids(scenes)
        return [s for s in scenes if s["scene_id"] not in companion_ids]

    async def activate_scene(self, scene_id: int) -> None:
        """Activates a lighting scene, ramping its loads to their scene levels.

        The command is sent asynchronously and returns before the ramp
        completes, so a scene's `is_active` may not have changed yet if
        `get_scenes()` is called immediately afterwards.

        Parameters:
            `scene_id` - (int) The scene's `scene_id`, as reported by
                         `get_scenes()`
        """
        item_id = await self._get_item_id()
        await self.director.send_post_request(
            f"/api/v1/items/{item_id}/commands",
            "ACTIVATE_SCENE",
            {"SCENE_ID": scene_id},
        )

    async def deactivate_scene(self, scene_id: int) -> None:
        """Deactivates a lighting scene, releasing its loads. This releases the
        scene rather than restoring the levels its loads held beforehand.

        Parameters:
            `scene_id` - (int) The scene's `scene_id`, as reported by
                         `get_scenes()`
        """
        item_id = await self._get_item_id()
        await self.director.send_post_request(
            f"/api/v1/items/{item_id}/commands",
            "DEACTIVATE_SCENE",
            {"SCENE_ID": scene_id},
        )

    async def toggle_scene(self, scene_id: int) -> None:
        """Toggles a lighting scene between activated and deactivated.

        Parameters:
            `scene_id` - (int) The scene's `scene_id`, as reported by
                         `get_scenes()`
        """
        item_id = await self._get_item_id()
        await self.director.send_post_request(
            f"/api/v1/items/{item_id}/commands",
            "TOGGLE_SCENE",
            {"SCENE_ID": scene_id},
        )
