import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from src.app.services.iam_service import IAMService
from src.app.exceptions.exceptions import BadRequestError


@pytest.fixture
def mock_repository():
    repo = AsyncMock()
    return repo


@pytest.mark.asyncio
@patch("src.app.services.iam_service.block_user_auth", new_callable=AsyncMock)
async def test_block_user_blocks_user(mock_block_user_auth, mock_repository):
    mock_repository.create_log.return_value = "log_created"
    service = IAMService(mock_repository)
    user_id = "user123"
    to_block = True

    result = await service.block_user(user_id, to_block)

    mock_block_user_auth.assert_awaited_once_with(user_id, to_block)
    mock_repository.create_log.assert_awaited_once_with(user_id, "block")
    assert result == "log_created"


@pytest.mark.asyncio
@patch("src.app.services.iam_service.block_user_auth", new_callable=AsyncMock)
async def test_block_user_unblocks_user(mock_block_user_auth, mock_repository):
    mock_repository.create_log.return_value = "log_created"
    service = IAMService(mock_repository)
    user_id = "user123"
    to_block = False

    result = await service.block_user(user_id, to_block)

    mock_block_user_auth.assert_awaited_once_with(user_id, to_block)
    mock_repository.create_log.assert_awaited_once_with(user_id, "unblock")
    assert result == "log_created"


@pytest.mark.asyncio
@patch("src.app.services.iam_service.change_rol_auth", new_callable=AsyncMock)
async def test_change_role(mock_change_rol_auth, mock_repository):
    mock_repository.create_log.return_value = "log_created"
    service = IAMService(mock_repository)
    user_id = "user123"
    rol = "student"

    result = await service.change_role(user_id, rol)

    mock_change_rol_auth.assert_awaited_once_with(user_id, rol)
    mock_repository.create_log.assert_awaited_once_with(user_id, rol)
    assert result == "log_created"


@pytest.mark.asyncio
async def test_assert_is_a_possible_role_accepts_valid_roles(mock_repository):
    service = IAMService(mock_repository)
    # Should not raise for valid roles
    await service.assertIsAPossibleRole("student")
    await service.assertIsAPossibleRole("teacher")


@pytest.mark.asyncio
async def test_assert_is_a_possible_role_raises_for_invalid_role(mock_repository):
    service = IAMService(mock_repository)
    with pytest.raises(BadRequestError):
        await service.assertIsAPossibleRole("admin")
    with pytest.raises(BadRequestError):
        await service.assertIsAPossibleRole("")
    with pytest.raises(BadRequestError):
        await service.assertIsAPossibleRole("STUDENT")
