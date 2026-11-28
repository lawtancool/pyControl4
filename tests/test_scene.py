"""Tests for C4AdvancedLighting — scene listing and scene commands."""

import json
from unittest.mock import AsyncMock, patch

import pytest

from pyControl4.error_handling import NotFound
from pyControl4.scene import (
    ADVANCED_LIGHTING_PROXY,
    ADVANCED_LIGHTING_URI,
    C4AdvancedLighting,
    find_advanced_lighting_agent,
)

AGENT_ITEM_ID = 3

# What the Director reports: the agent among ordinary items.
ALL_ITEMS = [
    {"id": 7, "name": "Kitchen Lights", "proxy": "light"},
    {
        "id": AGENT_ITEM_ID,
        "name": "Advanced Lighting",
        "proxy": ADVANCED_LIGHTING_PROXY,
    },
]
ITEMS_WITHOUT_AGENT = [{"id": 7, "name": "Kitchen Lights", "proxy": "light"}]

SCENES_RESPONSE = json.dumps(
    [
        {
            "scene_id": 0,
            "name": "Movie Night",
            "ramp_capable": True,
            "is_active": False,
            "full_on": False,
            "full_off": False,
            "user_defined": True,
            "lock_loads": False,
        },
        {
            "scene_id": 18,
            "name": "Office Mellow",
            "ramp_capable": True,
            "is_active": True,
            "full_on": False,
            "full_off": False,
            "user_defined": False,
            "lock_loads": True,
        },
    ]
)


def _scene(scene_id, name, is_active=False, **extra):
    """Builds one scene as the Advanced Lighting agent reports it."""
    return {
        "scene_id": scene_id,
        "name": name,
        "ramp_capable": True,
        "is_active": is_active,
        "full_on": False,
        "full_off": False,
        "user_defined": extra.get("user_defined", False),
        "lock_loads": extra.get("lock_loads", False),
    }


# A Composer-built system: base scenes with generated companions at id + 1,
# including the trailing-space names that occur in practice.
PAIRED_SCENES_RESPONSE = json.dumps(
    [
        _scene(0, "Tv time best", user_defined=True),
        _scene(6, "Good morning", lock_loads=True),
        _scene(7, "Good morning (Toggle)"),
        _scene(8, "Good morning ", lock_loads=True),
        _scene(9, "Good morning  (Toggle)"),
        _scene(18, "Office mellow", is_active=True, lock_loads=True),
        _scene(19, "Office mellow (Toggle)", is_active=True),
    ]
)


@pytest.mark.asyncio
async def test_get_scenes_returns_parsed(director):
    """get_scenes returns a parsed list of scene dictionaries."""
    agent = C4AdvancedLighting(director, AGENT_ITEM_ID)
    with patch.object(
        director, "send_get_request", new=AsyncMock(return_value=SCENES_RESPONSE)
    ):
        result = await agent.get_scenes()
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]["name"] == "Movie Night"
    assert result[1]["scene_id"] == 18


@pytest.mark.asyncio
async def test_get_scenes_uses_agent_uri(director):
    """Scenes are listed from the fixed agent endpoint, not an item path."""
    agent = C4AdvancedLighting(director, AGENT_ITEM_ID)
    mock = AsyncMock(return_value=SCENES_RESPONSE)
    with patch.object(director, "send_get_request", new=mock):
        await agent.get_scenes()
    assert mock.call_args[0][0] == ADVANCED_LIGHTING_URI


@pytest.mark.asyncio
async def test_get_scenes_reports_is_active(director):
    """is_active passes through as a bool for both states."""
    agent = C4AdvancedLighting(director, AGENT_ITEM_ID)
    with patch.object(
        director, "send_get_request", new=AsyncMock(return_value=SCENES_RESPONSE)
    ):
        result = await agent.get_scenes()
    assert result[0]["is_active"] is False
    assert result[1]["is_active"] is True


@pytest.mark.asyncio
async def test_get_scenes_empty(director):
    """A system with no scenes returns an empty list rather than raising."""
    agent = C4AdvancedLighting(director, AGENT_ITEM_ID)
    with patch.object(director, "send_get_request", new=AsyncMock(return_value="[]")):
        result = await agent.get_scenes()
    assert result == []


@pytest.mark.asyncio
async def test_activate_scene(director):
    """activate_scene posts ACTIVATE_SCENE to the agent's item path."""
    agent = C4AdvancedLighting(director, AGENT_ITEM_ID)
    mock = AsyncMock(return_value="{}")
    with patch.object(director, "send_post_request", new=mock):
        await agent.activate_scene(18)
    uri, command, params = mock.call_args[0]
    assert uri == f"/api/v1/items/{AGENT_ITEM_ID}/commands"
    assert command == "ACTIVATE_SCENE"
    assert params == {"SCENE_ID": 18}


@pytest.mark.asyncio
async def test_deactivate_scene(director):
    """deactivate_scene posts DEACTIVATE_SCENE to the agent's item path."""
    agent = C4AdvancedLighting(director, AGENT_ITEM_ID)
    mock = AsyncMock(return_value="{}")
    with patch.object(director, "send_post_request", new=mock):
        await agent.deactivate_scene(18)
    uri, command, params = mock.call_args[0]
    assert uri == f"/api/v1/items/{AGENT_ITEM_ID}/commands"
    assert command == "DEACTIVATE_SCENE"
    assert params == {"SCENE_ID": 18}


@pytest.mark.asyncio
async def test_toggle_scene(director):
    """toggle_scene posts TOGGLE_SCENE to the agent's item path."""
    agent = C4AdvancedLighting(director, AGENT_ITEM_ID)
    mock = AsyncMock(return_value="{}")
    with patch.object(director, "send_post_request", new=mock):
        await agent.toggle_scene(18)
    uri, command, params = mock.call_args[0]
    assert uri == f"/api/v1/items/{AGENT_ITEM_ID}/commands"
    assert command == "TOGGLE_SCENE"
    assert params == {"SCENE_ID": 18}


@pytest.mark.asyncio
async def test_activate_scene_id_zero(director):
    """scene_id 0 is a valid id and must not be treated as absent."""
    agent = C4AdvancedLighting(director, AGENT_ITEM_ID)
    mock = AsyncMock(return_value="{}")
    with patch.object(director, "send_post_request", new=mock):
        await agent.activate_scene(0)
    assert mock.call_args[0][2] == {"SCENE_ID": 0}


@pytest.mark.asyncio
async def test_item_id_coerced_to_int(director):
    """C4Entity coerces the agent item id, so string ids build a valid URI."""
    agent = C4AdvancedLighting(director, "3")
    mock = AsyncMock(return_value="{}")
    with patch.object(director, "send_post_request", new=mock):
        await agent.activate_scene(18)
    assert mock.call_args[0][0] == "/api/v1/items/3/commands"


@pytest.mark.asyncio
async def test_get_scenes_omits_toggle_companions(director):
    """Generated `(Toggle)` companions are left out of the default listing."""
    agent = C4AdvancedLighting(director, AGENT_ITEM_ID)
    with patch.object(
        director, "send_get_request", new=AsyncMock(return_value=PAIRED_SCENES_RESPONSE)
    ):
        result = await agent.get_scenes()
    assert [s["scene_id"] for s in result] == [0, 6, 8, 18]


@pytest.mark.asyncio
async def test_get_scenes_can_include_toggle_companions(director):
    """include_toggle_companions returns everything the agent reports."""
    agent = C4AdvancedLighting(director, AGENT_ITEM_ID)
    with patch.object(
        director, "send_get_request", new=AsyncMock(return_value=PAIRED_SCENES_RESPONSE)
    ):
        result = await agent.get_scenes(include_toggle_companions=True)
    assert [s["scene_id"] for s in result] == [0, 6, 7, 8, 9, 18, 19]


@pytest.mark.asyncio
async def test_toggle_companion_matched_on_exact_name(director):
    """A companion of a trailing-space name is matched, not its neighbour.

    Scene 8 is "Good morning " and its companion 9 is "Good morning  (Toggle)"
    -- two spaces. Stripping names would make 9 look like the companion of
    scene 6, "Good morning", whose own companion is 7.
    """
    agent = C4AdvancedLighting(director, AGENT_ITEM_ID)
    with patch.object(
        director, "send_get_request", new=AsyncMock(return_value=PAIRED_SCENES_RESPONSE)
    ):
        result = await agent.get_scenes()
    assert {s["name"] for s in result} == {
        "Tv time best",
        "Good morning",
        "Good morning ",
        "Office mellow",
    }


@pytest.mark.asyncio
async def test_user_named_toggle_scene_is_kept(director):
    """A scene a user happened to name "(Toggle)" is not filtered.

    Nothing sits at its `scene_id` - 1, so the id half of the pattern fails and
    the scene is left in the list.
    """
    response = json.dumps([_scene(4, "Movie (Toggle)", user_defined=True)])
    agent = C4AdvancedLighting(director, AGENT_ITEM_ID)
    with patch.object(
        director, "send_get_request", new=AsyncMock(return_value=response)
    ):
        result = await agent.get_scenes()
    assert [s["scene_id"] for s in result] == [4]


@pytest.mark.asyncio
async def test_orphan_toggle_companion_is_kept(director):
    """A companion whose base scene is missing is left in the list.

    Hiding it would mean dropping the only scene reported for that name.
    """
    response = json.dumps([_scene(19, "Office mellow (Toggle)")])
    agent = C4AdvancedLighting(director, AGENT_ITEM_ID)
    with patch.object(
        director, "send_get_request", new=AsyncMock(return_value=response)
    ):
        result = await agent.get_scenes()
    assert [s["scene_id"] for s in result] == [19]


@pytest.mark.asyncio
async def test_find_advanced_lighting_agent(director):
    """The agent is found by its proxy, whatever its item id is."""
    with patch.object(
        director, "get_all_item_info", new=AsyncMock(return_value=ALL_ITEMS)
    ):
        assert await find_advanced_lighting_agent(director) == AGENT_ITEM_ID


@pytest.mark.asyncio
async def test_find_advanced_lighting_agent_absent(director):
    """A system with no Advanced Lighting agent returns None, not an error."""
    with patch.object(
        director, "get_all_item_info", new=AsyncMock(return_value=ITEMS_WITHOUT_AGENT)
    ):
        assert await find_advanced_lighting_agent(director) is None


@pytest.mark.asyncio
async def test_item_id_looked_up_on_first_command(director):
    """Constructed without an item id, the agent finds its own."""
    agent = C4AdvancedLighting(director)
    assert agent.item_id is None
    post = AsyncMock(return_value="{}")
    with (
        patch.object(
            director, "get_all_item_info", new=AsyncMock(return_value=ALL_ITEMS)
        ),
        patch.object(director, "send_post_request", new=post),
    ):
        await agent.activate_scene(18)
    assert post.call_args[0][0] == f"/api/v1/items/{AGENT_ITEM_ID}/commands"
    assert agent.item_id == AGENT_ITEM_ID


@pytest.mark.asyncio
async def test_item_id_looked_up_only_once(director):
    """The lookup is cached, so later commands cost one request, not two."""
    agent = C4AdvancedLighting(director)
    items = AsyncMock(return_value=ALL_ITEMS)
    with (
        patch.object(director, "get_all_item_info", new=items),
        patch.object(director, "send_post_request", new=AsyncMock(return_value="{}")),
    ):
        await agent.activate_scene(18)
        await agent.deactivate_scene(18)
        await agent.toggle_scene(18)
    items.assert_awaited_once()


@pytest.mark.asyncio
async def test_explicit_item_id_skips_lookup(director):
    """An item id passed in is used as given, with no item listing fetched."""
    agent = C4AdvancedLighting(director, AGENT_ITEM_ID)
    items = AsyncMock(return_value=ALL_ITEMS)
    post = AsyncMock(return_value="{}")
    with (
        patch.object(director, "get_all_item_info", new=items),
        patch.object(director, "send_post_request", new=post),
    ):
        await agent.activate_scene(18)
    items.assert_not_awaited()
    assert post.call_args[0][0] == f"/api/v1/items/{AGENT_ITEM_ID}/commands"


@pytest.mark.asyncio
async def test_command_without_agent_raises_not_found(director):
    """Commanding a system that has no agent raises rather than posting."""
    agent = C4AdvancedLighting(director)
    post = AsyncMock(return_value="{}")
    with (
        patch.object(
            director,
            "get_all_item_info",
            new=AsyncMock(return_value=ITEMS_WITHOUT_AGENT),
        ),
        patch.object(director, "send_post_request", new=post),
    ):
        with pytest.raises(NotFound):
            await agent.activate_scene(18)
    post.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_scenes_needs_no_item_id(director):
    """Listing scenes uses the fixed agent endpoint, so it needs no lookup."""
    agent = C4AdvancedLighting(director)
    items = AsyncMock(return_value=ALL_ITEMS)
    with (
        patch.object(director, "get_all_item_info", new=items),
        patch.object(
            director, "send_get_request", new=AsyncMock(return_value=SCENES_RESPONSE)
        ),
    ):
        result = await agent.get_scenes()
    assert len(result) == 2
    items.assert_not_awaited()
    assert agent.item_id is None
