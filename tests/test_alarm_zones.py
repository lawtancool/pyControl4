"""Tests for C4SecurityPanel zone methods and C4ZoneType."""

import json
from unittest.mock import AsyncMock, patch

import pytest

from pyControl4.alarm import C4SecurityPanel, C4ZoneType


@pytest.mark.asyncio
async def test_get_zones_returns_zone_list(director):
    """Test that get_zones returns a list of zones."""
    zones_response = json.dumps({
        "zones": {
            "zone": [
                {
                    "id": 1,
                    "name": "Front Door",
                    "room_id": 100,
                    "room_name": "Living Room",
                    "type_id": 2,
                    "is_open": False,
                    "is_bypassed": False,
                    "is_chimeable": True,
                    "can_bypass": True,
                    "can_control": True,
                },
                {
                    "id": 2,
                    "name": "Back Window",
                    "room_id": 101,
                    "room_name": "Kitchen",
                    "type_id": 3,
                    "is_open": True,
                    "is_bypassed": False,
                    "is_chimeable": False,
                    "can_bypass": True,
                    "can_control": False,
                },
            ]
        }
    })

    with patch.object(
        director, "send_post_request", new=AsyncMock(return_value=zones_response)
    ):
        panel = C4SecurityPanel(director, 500)
        zones = await panel.get_zones()

    assert zones is not None
    assert len(zones) == 2
    assert zones[0]["name"] == "Front Door"
    assert zones[0]["type_id"] == 2
    assert zones[0]["is_open"] is False
    assert zones[1]["name"] == "Back Window"
    assert zones[1]["is_open"] is True


@pytest.mark.asyncio
async def test_get_zones_single_zone(director):
    """Test that get_zones handles a single zone response (returned as dict not list)."""
    zones_response = json.dumps({
        "zones": {
            "zone": {
                "id": 1,
                "name": "Front Door",
                "type_id": 2,
                "is_open": False,
            }
        }
    })

    with patch.object(
        director, "send_post_request", new=AsyncMock(return_value=zones_response)
    ):
        panel = C4SecurityPanel(director, 500)
        zones = await panel.get_zones()

    assert zones is not None
    assert len(zones) == 1
    assert zones[0]["name"] == "Front Door"


@pytest.mark.asyncio
async def test_get_zones_empty(director):
    """Test that get_zones handles empty zone list."""
    zones_response = json.dumps({"zones": {"zone": []}})

    with patch.object(
        director, "send_post_request", new=AsyncMock(return_value=zones_response)
    ):
        panel = C4SecurityPanel(director, 500)
        zones = await panel.get_zones()

    assert zones is not None
    assert len(zones) == 0


@pytest.mark.asyncio
async def test_get_zones_no_zones_key(director):
    """Test that get_zones handles response without zones key."""
    zones_response = json.dumps({})

    with patch.object(
        director, "send_post_request", new=AsyncMock(return_value=zones_response)
    ):
        panel = C4SecurityPanel(director, 500)
        zones = await panel.get_zones()

    assert zones is not None
    assert len(zones) == 0


@pytest.mark.asyncio
async def test_get_zones_invalid_json(director):
    """Test that get_zones handles invalid JSON response."""
    with patch.object(
        director, "send_post_request", new=AsyncMock(return_value="not json")
    ):
        panel = C4SecurityPanel(director, 500)
        zones = await panel.get_zones()

    assert zones is None


@pytest.mark.asyncio
async def test_get_zones_sends_correct_command(director):
    """Test that get_zones sends the correct command."""
    zones_response = json.dumps({"zones": {"zone": []}})
    mock = AsyncMock(return_value=zones_response)

    with patch.object(director, "send_post_request", new=mock):
        panel = C4SecurityPanel(director, 500)
        await panel.get_zones()

    mock.assert_called_once_with(
        "/api/v1/items/500/commands",
        "GET_ZONE_LIST",
        {},
        is_async=False,
    )


@pytest.mark.asyncio
async def test_get_open_zones(director):
    """Test that get_open_zones returns only open zones."""
    zones_response = json.dumps({
        "zones": {
            "zone": [
                {"id": 2, "name": "Back Window", "is_open": True},
            ]
        }
    })

    with patch.object(
        director, "send_post_request", new=AsyncMock(return_value=zones_response)
    ):
        panel = C4SecurityPanel(director, 500)
        zones = await panel.get_open_zones()

    assert zones is not None
    assert len(zones) == 1
    assert zones[0]["name"] == "Back Window"


@pytest.mark.asyncio
async def test_get_open_zones_sends_correct_command(director):
    """Test that get_open_zones sends the correct command."""
    zones_response = json.dumps({"zones": {"zone": []}})
    mock = AsyncMock(return_value=zones_response)

    with patch.object(director, "send_post_request", new=mock):
        panel = C4SecurityPanel(director, 500)
        await panel.get_open_zones()

    mock.assert_called_once_with(
        "/api/v1/items/500/commands",
        "GET_OPEN_ZONE_LIST",
        {},
        is_async=False,
    )


class TestC4ZoneType:
    """Tests for C4ZoneType enum."""

    def test_zone_type_values(self):
        """Test that zone type enum has correct values."""
        assert C4ZoneType.UNKNOWN == 0
        assert C4ZoneType.CONTACT_SENSOR == 1
        assert C4ZoneType.EXTERIOR_DOOR == 2
        assert C4ZoneType.EXTERIOR_WINDOW == 3
        assert C4ZoneType.INTERIOR_DOOR == 4
        assert C4ZoneType.MOTION_SENSOR == 5
        assert C4ZoneType.FIRE == 6
        assert C4ZoneType.GAS == 7
        assert C4ZoneType.CO == 8
        assert C4ZoneType.HEAT == 9
        assert C4ZoneType.WATER == 10
        assert C4ZoneType.SMOKE == 11
        assert C4ZoneType.PRESSURE == 12
        assert C4ZoneType.GLASS_BREAK == 13
        assert C4ZoneType.GATE == 14
        assert C4ZoneType.GARAGE == 15
        assert C4ZoneType.COLD == 16

    def test_get_name_known_types(self):
        """Test get_name returns correct names for known types."""
        assert C4ZoneType.get_name(2) == "Exterior Door"
        assert C4ZoneType.get_name(3) == "Exterior Window"
        assert C4ZoneType.get_name(5) == "Motion Sensor"
        assert C4ZoneType.get_name(6) == "Fire Sensor"
        assert C4ZoneType.get_name(10) == "Water Sensor"
        assert C4ZoneType.get_name(15) == "Garage Door Sensor"

    def test_get_name_unknown_type(self):
        """Test get_name returns default for unknown types."""
        assert C4ZoneType.get_name(99) == "Security Zone"
        assert C4ZoneType.get_name(-1) == "Security Zone"
