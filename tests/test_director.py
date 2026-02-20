"""Tests for C4Director — get_item_variable_value, get_all_item_variable_value,
and basic request wrappers.
"""

import json
from unittest.mock import AsyncMock, patch

import pytest


@pytest.mark.asyncio
async def test_get_item_variable_value_int(director):
    """Normal integer value is returned as-is."""
    response = json.dumps([{"id": 100, "varName": "LIGHT_LEVEL", "value": 75}])
    with patch.object(
        director, "send_get_request", new=AsyncMock(return_value=response)
    ):
        result = await director.get_item_variable_value(100, "LIGHT_LEVEL")
    assert result == 75


@pytest.mark.asyncio
async def test_get_item_variable_value_zero(director):
    """Zero is returned as 0, not confused with None or falsy."""
    response = json.dumps([{"id": 100, "varName": "LIGHT_LEVEL", "value": 0}])
    with patch.object(
        director, "send_get_request", new=AsyncMock(return_value=response)
    ):
        result = await director.get_item_variable_value(100, "LIGHT_LEVEL")
    assert result == 0
    assert result is not None


@pytest.mark.asyncio
async def test_get_item_variable_value_bool(director):
    """Boolean value is returned as a Python bool."""
    response = json.dumps([{"id": 100, "varName": "IS_ON", "value": True}])
    with patch.object(
        director, "send_get_request", new=AsyncMock(return_value=response)
    ):
        result = await director.get_item_variable_value(100, "IS_ON")
    assert result is True


@pytest.mark.asyncio
async def test_get_item_variable_value_string(director):
    """String value is returned as-is."""
    response = json.dumps(
        [{"id": 100, "varName": "PARTITION_STATE", "value": "ARMED_AWAY"}]
    )
    with patch.object(
        director, "send_get_request", new=AsyncMock(return_value=response)
    ):
        result = await director.get_item_variable_value(100, "PARTITION_STATE")
    assert result == "ARMED_AWAY"


@pytest.mark.asyncio
async def test_get_item_variable_value_null(director):
    """JSON null value passes through as None (distinct from 'Undefined')."""
    response = json.dumps([{"id": 100, "varName": "OPTIONAL_VAR", "value": None}])
    with patch.object(
        director, "send_get_request", new=AsyncMock(return_value=response)
    ):
        result = await director.get_item_variable_value(100, "OPTIONAL_VAR")
    assert result is None


@pytest.mark.asyncio
async def test_get_item_variable_value_empty_response(director):
    """Empty list response raises ValueError."""
    with patch.object(director, "send_get_request", new=AsyncMock(return_value="[]")):
        with pytest.raises(ValueError):
            await director.get_item_variable_value(100, "NONEXISTENT")


@pytest.mark.asyncio
async def test_get_item_variable_value_invalid_format(director):
    """Non-list JSON response raises ValueError (2.0 guard)."""
    with patch.object(
        director, "send_get_request", new=AsyncMock(return_value='{"value": 1}')
    ):
        with pytest.raises(ValueError):
            await director.get_item_variable_value(100, "TEST")


@pytest.mark.asyncio
async def test_get_item_variable_value_list_var_name(director):
    """List of var_names is joined with comma in the request URI."""
    response = json.dumps([{"id": 100, "varName": "A", "value": 1}])
    mock = AsyncMock(return_value=response)
    with patch.object(director, "send_get_request", new=mock):
        await director.get_item_variable_value(100, ["A", "B"])
    uri = mock.call_args[0][0]
    assert "varnames=A,B" in uri


@pytest.mark.asyncio
async def test_get_item_variable_value_tuple_var_name(director):
    """Tuple of var_names is joined with comma in the request URI."""
    response = json.dumps([{"id": 100, "varName": "X", "value": 42}])
    mock = AsyncMock(return_value=response)
    with patch.object(director, "send_get_request", new=mock):
        await director.get_item_variable_value(100, ("X", "Y"))
    uri = mock.call_args[0][0]
    assert "varnames=X,Y" in uri


@pytest.mark.asyncio
async def test_get_all_item_variable_value_mixed(director):
    """get_all_item_variable_value normalizes Undefined values in-place."""
    response = json.dumps(
        [
            {"id": 1, "varName": "HUMIDITY", "value": "Undefined"},
            {"id": 2, "varName": "HUMIDITY", "value": 45},
            {"id": 3, "varName": "HUMIDITY", "value": 0},
        ]
    )
    with patch.object(
        director, "send_get_request", new=AsyncMock(return_value=response)
    ):
        result = await director.get_all_item_variable_value("HUMIDITY")
    assert result[0]["value"] is None
    assert result[1]["value"] == 45
    assert result[2]["value"] == 0


@pytest.mark.asyncio
async def test_get_all_item_variable_value_empty(director):
    """Empty list response raises ValueError."""
    with patch.object(director, "send_get_request", new=AsyncMock(return_value="[]")):
        with pytest.raises(ValueError):
            await director.get_all_item_variable_value("NONEXISTENT")


@pytest.mark.asyncio
async def test_get_all_item_info_returns_parsed(director):
    """get_all_item_info returns parsed list (2.0 returns parsed JSON)."""
    raw = '[{"id": 1, "name": "Light"}]'
    with patch.object(director, "send_get_request", new=AsyncMock(return_value=raw)):
        result = await director.get_all_item_info()
    assert isinstance(result, list)
    assert result[0]["id"] == 1
