"""Tests for SSL context passthrough in C4Websocket."""

import ssl
from unittest.mock import AsyncMock, MagicMock, patch, call

import aiohttp
import socketio_v4
import pytest

from pyControl4.websocket import C4Websocket


def test_default_no_ssl_context():
    """Test that C4Websocket defaults to no ssl_context (backward compat)."""
    ws = C4Websocket("192.168.1.1")
    assert ws.ssl_context is None


def test_ssl_context_stored():
    """Test that a provided ssl_context is stored."""
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    ws = C4Websocket("192.168.1.1", ssl_context=ctx)
    assert ws.ssl_context is ctx


@pytest.mark.asyncio
async def test_sio_connect_without_ssl_context():
    """Test that sio_connect uses ssl_verify=False when no ssl_context."""
    ws = C4Websocket("192.168.1.1")
    with patch.object(socketio_v4.AsyncClient, "__init__", return_value=None) as mock_init, \
         patch.object(socketio_v4.AsyncClient, "register_namespace"), \
         patch.object(socketio_v4.AsyncClient, "connect", new_callable=AsyncMock):
        await ws.sio_connect("test-token")
        mock_init.assert_called_once_with(ssl_verify=False)


@pytest.mark.asyncio
async def test_sio_connect_with_ssl_context():
    """Test that sio_connect uses ssl_verify=True and http_session when
    ssl_context is provided."""
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    ws = C4Websocket("192.168.1.1", ssl_context=ctx)
    with patch.object(socketio_v4.AsyncClient, "__init__", return_value=None) as mock_init, \
         patch.object(socketio_v4.AsyncClient, "register_namespace"), \
         patch.object(socketio_v4.AsyncClient, "connect", new_callable=AsyncMock), \
         patch.object(aiohttp, "TCPConnector") as mock_connector_cls, \
         patch.object(aiohttp, "ClientSession") as mock_session_cls:
        mock_conn = MagicMock()
        mock_connector_cls.return_value = mock_conn
        mock_sess = MagicMock()
        mock_session_cls.return_value = mock_sess
        await ws.sio_connect("test-token")
        mock_connector_cls.assert_called_once_with(ssl=ctx)
        mock_session_cls.assert_called_once_with(connector=mock_conn)
        mock_init.assert_called_once_with(
            ssl_verify=True, http_session=mock_sess
        )
