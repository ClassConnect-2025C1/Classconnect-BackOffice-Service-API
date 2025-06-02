import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.app.services.admin_service import AdminService
from src.app.exceptions.exceptions import (
    AdminNotFoundError,
    AdminAlreadyExistsError,
    WrongPasswordError,
)


@pytest.fixture
def mock_repository():
    repo = MagicMock()
    repo.get_by_email = AsyncMock()
    repo.get_by_id = AsyncMock()
    repo.create = AsyncMock()
    return repo


@pytest.mark.asyncio
@patch("src.app.services.admin_service.hash_password", return_value="hashed_pw")
async def test_create_admin_success(mock_hash, mock_repository):
    mock_repository.get_by_id.return_value = {"id": "creator_id"}
    mock_repository.get_by_email.return_value = None
    mock_repository.create.return_value = {"email": "admin@example.com"}
    service = AdminService(mock_repository)

    result = await service.create_admin("admin@example.com", "password", "creator_id")

    mock_repository.get_by_id.assert_called_once_with("creator_id")
    mock_repository.get_by_email.assert_called_once_with("admin@example.com")
    mock_hash.assert_called_once_with("password")
    mock_repository.create.assert_awaited_once_with(
        "admin@example.com", "hashed_pw", "creator_id"
    )
    assert result == {"email": "admin@example.com"}


@pytest.mark.asyncio
@patch("src.app.services.admin_service.hash_password", return_value="hashed_pw")
async def test_create_admin_creator_not_found(mock_hash, mock_repository):
    mock_repository.get_by_id.return_value = None
    service = AdminService(mock_repository)

    with pytest.raises(AdminNotFoundError):
        await service.create_admin("admin@example.com", "password", "creator_id")


@pytest.mark.asyncio
@patch("src.app.services.admin_service.hash_password", return_value="hashed_pw")
async def test_create_admin_email_already_exists(mock_hash, mock_repository):
    mock_repository.get_by_id.return_value = {"id": "creator_id"}
    mock_repository.get_by_email.return_value = {"email": "admin@example.com"}
    service = AdminService(mock_repository)

    with pytest.raises(AdminAlreadyExistsError):
        await service.create_admin("admin@example.com", "password", "creator_id")


@pytest.mark.asyncio
async def test_assert_admin_email_not_exist_raises(mock_repository):
    mock_repository.get_by_email.return_value = {"email": "admin@example.com"}
    service = AdminService(mock_repository)
    with pytest.raises(AdminAlreadyExistsError):
        await service.assertAdminEmailNotExist("admin@example.com")


@pytest.mark.asyncio
async def test_assert_admin_email_not_exist_ok(mock_repository):
    mock_repository.get_by_email.return_value = None
    service = AdminService(mock_repository)
    await service.assertAdminEmailNotExist("admin@example.com")


@pytest.mark.asyncio
async def test_assert_admin_id_exist_raises(mock_repository):
    mock_repository.get_by_id.return_value = None
    service = AdminService(mock_repository)
    with pytest.raises(AdminNotFoundError):
        await service.assertAdminIDExist("creator_id")


@pytest.mark.asyncio
async def test_assert_admin_id_exist_ok(mock_repository):
    mock_repository.get_by_id.return_value = {"id": "creator_id"}
    service = AdminService(mock_repository)
    await service.assertAdminIDExist("creator_id")


@pytest.mark.asyncio
@patch("src.app.services.admin_service.verify_password")
async def test_login_admin_success(mock_verify, mock_repository):
    # Setup
    admin_obj = MagicMock()
    admin_obj.hashed_password = "hashed_pw"
    mock_repository.get_by_email = AsyncMock(return_value=admin_obj)
    mock_verify.return_value = True
    service = AdminService(mock_repository)

    result = await service.login_admin("admin@example.com", "password")

    mock_repository.get_by_email.assert_awaited_once_with("admin@example.com")
    mock_verify.assert_called_once_with("password", "hashed_pw")
    assert result == admin_obj


@pytest.mark.asyncio
@patch("src.app.services.admin_service.verify_password")
async def test_login_admin_not_found(mock_verify, mock_repository):
    mock_repository.get_by_email = AsyncMock(return_value=None)
    service = AdminService(mock_repository)

    with pytest.raises(AdminNotFoundError):
        await service.login_admin("admin@example.com", "password")
    mock_repository.get_by_email.assert_awaited_once_with("admin@example.com")
    mock_verify.assert_not_called()


@pytest.mark.asyncio
@patch("src.app.services.admin_service.verify_password")
async def test_login_admin_wrong_password(mock_verify, mock_repository):
    admin_obj = MagicMock()
    admin_obj.hashed_password = "hashed_pw"
    mock_repository.get_by_email = AsyncMock(return_value=admin_obj)
    mock_verify.return_value = False
    service = AdminService(mock_repository)

    with pytest.raises(WrongPasswordError):
        await service.login_admin("admin@example.com", "wrongpassword")
    mock_repository.get_by_email.assert_awaited_once_with("admin@example.com")
    mock_verify.assert_called_once_with("wrongpassword", "hashed_pw")
