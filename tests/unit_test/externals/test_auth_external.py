import pytest
import os
import sys
from unittest.mock import patch, MagicMock, AsyncMock
from requests.exceptions import RequestException
from src.app.exceptions.exceptions import UserNotFoundError, BadRequestError
import types

import src.app.externals.auth_external as auth_external


async def fake_get_auth_url():
    return "http://fake-auth-service"


@pytest.fixture(autouse=True)
def set_env(monkeypatch):
    monkeypatch.setenv("URL_AUTH", "http://fake-auth-service")
    yield


@pytest.mark.asyncio
async def test_get_auth_url_success():
    url = await auth_external.get_auth_url()
    assert url == "http://fake-auth-service"


@pytest.mark.asyncio
async def test_get_auth_url_missing(monkeypatch):
    monkeypatch.delenv("URL_AUTH", raising=False)
    with pytest.raises(RuntimeError):
        await auth_external.get_auth_url()


@pytest.mark.asyncio
async def test_send_patch_request_success():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "OK"
    with patch(
        "src.app.externals.auth_external.requests.patch", return_value=mock_response
    ):
        result = await auth_external.send_patch_request(
            "user1", "http://fake/block/user1", {"block": True}
        )
        assert result is None


@pytest.mark.asyncio
async def test_send_patch_request_404():
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.text = "Not found"
    with patch(
        "src.app.externals.auth_external.requests.patch", return_value=mock_response
    ):
        with pytest.raises(UserNotFoundError):
            await auth_external.send_patch_request(
                "user2", "http://fake/block/user2", {"block": True}
            )


@pytest.mark.asyncio
async def test_send_patch_request_400():
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.text = "Bad request"
    with patch(
        "src.app.externals.auth_external.requests.patch", return_value=mock_response
    ):
        with pytest.raises(BadRequestError):
            await auth_external.send_patch_request(
                "user3", "http://fake/block/user3", {"block": True}
            )


@pytest.mark.asyncio
async def test_send_patch_request_exception():
    with patch(
        "src.app.externals.auth_external.requests.patch",
        side_effect=RequestException("Network error"),
    ):
        with pytest.raises(Exception) as excinfo:
            await auth_external.send_patch_request(
                "user4", "http://fake/block/user4", {"block": True}
            )
        assert "Auth service request failed" in str(excinfo.value)


@pytest.mark.asyncio
async def test_block_user_auth_calls_send_patch(monkeypatch):
    monkeypatch.setattr(
        auth_external,
        "get_auth_url",
        AsyncMock(return_value="http://fake-auth-service"),
    )
    send_patch_mock = AsyncMock(return_value=None)
    monkeypatch.setattr(auth_external, "send_patch_request", send_patch_mock)
    result = await auth_external.block_user_auth("user5", True)
    send_patch_mock.assert_awaited_with(
        "user5", "http://fake-auth-service/auth/block/user5", {"block": True}
    )
    assert result is None


@pytest.mark.asyncio
async def test_change_rol_auth_calls_send_patch(monkeypatch):
    monkeypatch.setattr(
        auth_external,
        "get_auth_url",
        AsyncMock(return_value="http://fake-auth-service"),
    )
    send_patch_mock = AsyncMock(return_value=None)
    monkeypatch.setattr(auth_external, "send_patch_request", send_patch_mock)
    result = await auth_external.change_rol_auth("user6", "admin")
    send_patch_mock.assert_awaited_with(
        "user6", "http://fake-auth-service/auth/rol/user6", {"role": "admin"}
    )
    assert result is None
