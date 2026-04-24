"""Tests for C4AdvancedLighting."""

import json
from unittest.mock import AsyncMock, call, patch

import pytest

from pyControl4.advanced_lighting import C4AdvancedLighting


SCENE_LIST = [
    {
        "scene_id": 1,
        "name": "Morning",
        "is_active": False,
        "ramp_capable": True,
        "full_on": False,
        "full_off": False,
        "user_defined": True,
        "lock_loads": False,
    },
    {
        "scene_id": 2,
        "name": "All Off",
        "is_active": False,
        "ramp_capable": False,
        "full_on": False,
        "full_off": True,
        "user_defined": False,
        "lock_loads": False,
    },
]

COMMANDS_RESPONSE = json.dumps([{"deviceId": 421, "command": "ACTIVATE_SCENE"}])
SCENES_RESPONSE = json.dumps(SCENE_LIST)


@pytest.mark.asyncio
async def test_create_fetches_agent_device_id(director):
    """create() fetches the agent device ID from the commands endpoint."""
    with patch.object(
        director, "send_get_request", new=AsyncMock(return_value=COMMANDS_RESPONSE)
    ):
        adv = await C4AdvancedLighting.create(director)
    assert adv.agent_device_id == 421


@pytest.mark.asyncio
async def test_create_raises_on_empty_commands(director):
    """create() raises ValueError when the Advanced Lighting agent is absent."""
    with patch.object(
        director, "send_get_request", new=AsyncMock(return_value="[]")
    ):
        with pytest.raises(ValueError, match="Advanced Lighting agent returned no commands"):
            await C4AdvancedLighting.create(director)


@pytest.mark.asyncio
async def test_get_scenes_returns_list(director):
    """get_scenes() returns the parsed list of scene dicts."""
    adv = C4AdvancedLighting(director, 421)
    with patch.object(
        director, "send_get_request", new=AsyncMock(return_value=SCENES_RESPONSE)
    ):
        scenes = await adv.get_scenes()
    assert len(scenes) == 2
    assert scenes[0]["scene_id"] == 1
    assert scenes[0]["name"] == "Morning"
    assert scenes[1]["full_off"] is True


@pytest.mark.asyncio
async def test_activate_scene_sends_correct_command(director):
    """activate_scene() POSTs ACTIVATE_SCENE with the correct scene ID."""
    adv = C4AdvancedLighting(director, 421)
    mock_post = AsyncMock(return_value="{}")
    with patch.object(director, "send_post_request", new=mock_post):
        await adv.activate_scene(1)
    mock_post.assert_called_once_with(
        "/api/v1/items/421/commands",
        "ACTIVATE_SCENE",
        {"SCENE_ID": 1},
    )


@pytest.mark.asyncio
async def test_deactivate_scene_sends_correct_command(director):
    """deactivate_scene() POSTs DEACTIVATE_SCENE with the correct scene ID."""
    adv = C4AdvancedLighting(director, 421)
    mock_post = AsyncMock(return_value="{}")
    with patch.object(director, "send_post_request", new=mock_post):
        await adv.deactivate_scene(2)
    mock_post.assert_called_once_with(
        "/api/v1/items/421/commands",
        "DEACTIVATE_SCENE",
        {"SCENE_ID": 2},
    )


@pytest.mark.asyncio
async def test_toggle_scene_sends_correct_command(director):
    """toggle_scene() POSTs TOGGLE_SCENE with the correct scene ID."""
    adv = C4AdvancedLighting(director, 421)
    mock_post = AsyncMock(return_value="{}")
    with patch.object(director, "send_post_request", new=mock_post):
        await adv.toggle_scene(1)
    mock_post.assert_called_once_with(
        "/api/v1/items/421/commands",
        "TOGGLE_SCENE",
        {"SCENE_ID": 1},
    )


@pytest.mark.asyncio
async def test_direct_constructor_agent_device_id(director):
    """Direct constructor stores agent_device_id as int."""
    adv = C4AdvancedLighting(director, "421")
    assert adv.agent_device_id == 421
    assert isinstance(adv.agent_device_id, int)
