"""Tests for handling of 'Undefined' variable values from the Control4 Director."""

import json
from unittest.mock import AsyncMock, patch

import pytest

from pyControl4.light import C4Light
from pyControl4.blind import C4Blind


@pytest.mark.asyncio
async def test_get_item_variable_value_undefined(director):
    """Test that get_item_variable_value normalizes 'Undefined' to None."""
    response = json.dumps([{"id": 123, "varName": "HUMIDITY", "value": "Undefined"}])
    with patch.object(
        director, "send_get_request", new=AsyncMock(return_value=response)
    ):
        result = await director.get_item_variable_value(123, "HUMIDITY")
    assert result is None


@pytest.mark.asyncio
async def test_get_all_item_variable_value_undefined(director):
    """Test that get_all_item_variable_value normalizes 'Undefined' to None in items."""
    response = json.dumps(
        [
            {"id": 100, "varName": "HUMIDITY", "value": "Undefined"},
            {"id": 100, "varName": "TEMPERATURE_F", "value": 72.5},
            {"id": 200, "varName": "HUMIDITY", "value": 45},
        ]
    )
    with patch.object(
        director, "send_get_request", new=AsyncMock(return_value=response)
    ):
        result = await director.get_all_item_variable_value("HUMIDITY,TEMPERATURE_F")
    assert result[0]["value"] is None
    assert result[1]["value"] == 72.5
    assert result[2]["value"] == 45


@pytest.mark.asyncio
async def test_light_get_level_undefined(director):
    """Test that int callers propagate None instead of crashing."""
    light = C4Light(director, 100)
    response = json.dumps([{"id": 100, "varName": "LIGHT_LEVEL", "value": "Undefined"}])
    with patch.object(
        director, "send_get_request", new=AsyncMock(return_value=response)
    ):
        result = await light.get_level()
    assert result is None


@pytest.mark.asyncio
async def test_blind_get_fully_open_undefined(director):
    """Test that bool callers propagate None instead of a misleading value."""
    blind = C4Blind(director, 200)
    response = json.dumps([{"id": 200, "varName": "Fully Open", "value": "Undefined"}])
    with patch.object(
        director, "send_get_request", new=AsyncMock(return_value=response)
    ):
        result = await blind.get_fully_open()
    assert result is None
