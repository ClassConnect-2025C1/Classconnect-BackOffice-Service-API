import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from src.app.services.admin_service import AdminService
from src.app.exceptions.exceptions import AdminNotFoundError, AdminAlreadyExistsError


@pytest.fixture
def mock_repository():
    repo = MagicMock()
    repo.get_by_email = MagicMock()
    repo.get_by_id = MagicMock()
    repo.create = AsyncMock()
    return repo


@pytest.mark.asyncio
@patch("src.app.services.admin_service.hash_password", return_value="hashed_pw")
async def test_create_admin_success(mock_hash, mock_repository):
    # Setup
    mock_repository.get_by_id.return_value = {"id": "creator_id"}
    mock_repository.get_by_email.return_value = None
    mock_repository.create.return_value = {"email": "admin@example.com"}
    service = AdminService(mock_repository)

    # Act
    result = await service.create_admin("admin@example.com", "password", "creator_id")

    # Assert
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


def test_assert_admin_email_not_exist_raises(mock_repository):
    mock_repository.get_by_email.return_value = {"email": "admin@example.com"}
    service = AdminService(mock_repository)
    with pytest.raises(AdminAlreadyExistsError):
        service.assertAdminEmailNotExist("admin@example.com")


def test_assert_admin_email_not_exist_ok(mock_repository):
    mock_repository.get_by_email.return_value = None
    service = AdminService(mock_repository)
    service.assertAdminEmailNotExist("admin@example.com")


def test_assert_admin_id_exist_raises(mock_repository):
    mock_repository.get_by_id.return_value = None
    service = AdminService(mock_repository)
    with pytest.raises(AdminNotFoundError):
        service.assertAdminIDExist("creator_id")


def test_assert_admin_id_exist_ok(mock_repository):
    mock_repository.get_by_id.return_value = {"id": "creator_id"}
    service = AdminService(mock_repository)
    service.assertAdminIDExist("creator_id")
