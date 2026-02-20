"""Tests for SSL context passthrough in C4Websocket."""

from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import socketio_v4
import pytest

from pyControl4.websocket import C4Websocket


@pytest.mark.asyncio
async def test_sio_connect_without_session():
    """Test that sio_connect uses ssl_verify=False without http_session when
    no session is provided."""
    ws = C4Websocket("192.168.1.1")
    with patch.object(
        socketio_v4.AsyncClient, "__init__", return_value=None
    ) as mock_init, patch.object(
        socketio_v4.AsyncClient, "register_namespace"
    ), patch.object(
        socketio_v4.AsyncClient, "connect", new_callable=AsyncMock
    ):
        await ws.sio_connect("test-token")
        mock_init.assert_called_once_with(ssl_verify=False)


@pytest.mark.asyncio
async def test_sio_connect_with_session():
    """Test that sio_connect creates a new session sharing the caller's
    connector and passes it as http_session, so engineio can safely close
    it without affecting the caller's session."""
    mock_connector = MagicMock()
    mock_session = MagicMock()
    mock_session.connector = mock_connector
    ws = C4Websocket("192.168.1.1", session_no_verify_ssl=mock_session)
    with patch.object(
        socketio_v4.AsyncClient, "__init__", return_value=None
    ) as mock_init, patch.object(
        socketio_v4.AsyncClient, "register_namespace"
    ), patch.object(
        socketio_v4.AsyncClient, "connect", new_callable=AsyncMock
    ), patch.object(
        aiohttp, "ClientSession"
    ) as mock_session_cls:
        mock_http_session = MagicMock()
        mock_session_cls.return_value = mock_http_session
        await ws.sio_connect("test-token")
        mock_session_cls.assert_called_once_with(
            connector=mock_connector, connector_owner=False
        )
        mock_init.assert_called_once_with(
            ssl_verify=False, http_session=mock_http_session
        )
