import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone
from bson import ObjectId
from src.app.repositories.admin_repository import AdminRepository
from src.app.entities.admin_data import AdminDTA


@pytest.fixture
def mock_collection():
    return AsyncMock()


@pytest.fixture
def mock_db(mock_collection):
    mock_db = MagicMock()
    mock_db.__getitem__.return_value = mock_collection
    return mock_db


@pytest.fixture
def repo(mock_db):
    return AdminRepository(mock_db)


@pytest.mark.asyncio
async def test_create_admin_success(repo, mock_collection):
    email = "admin@example.com"
    hashed_password = "hashed_pw"
    other_id = "other123"
    inserted_id = ObjectId()
    mock_collection.insert_one.return_value.inserted_id = inserted_id

    with patch(
        "src.app.repositories.admin_repository.datetime"
    ) as mock_datetime_module:
        now = datetime(2024, 1, 1, tzinfo=timezone.utc)
        mock_datetime_module.now.return_value = now
        result = await repo.create(email, hashed_password, other_id)

    assert isinstance(result, AdminDTA)
    assert result.id == str(inserted_id)
    assert result.email == email
    assert result.hashed_password == hashed_password
    assert result.signup_date == now
    assert result.other_id == other_id
    mock_collection.insert_one.assert_called_once()
    args, kwargs = mock_collection.insert_one.call_args
    assert args[0]["email"] == email
    assert args[0]["hashed_password"] == hashed_password
    assert args[0]["other_id"] == other_id
    assert isinstance(args[0]["signup_date"], datetime)


@pytest.mark.asyncio
async def test_get_by_id_success(repo, mock_collection):
    admin_id = str(ObjectId())
    admin_data = {
        "_id": ObjectId(admin_id),
        "email": "admin@example.com",
        "hashed_password": "hashed_pw",
        "signup_date": datetime(2024, 1, 1, tzinfo=timezone.utc),
        "other_id": "other123",
    }
    mock_collection.find_one.return_value = admin_data

    result = await repo.get_by_id(admin_id)

    assert isinstance(result, AdminDTA)
    assert result.id == admin_id
    assert result.email == admin_data["email"]
    assert result.hashed_password == admin_data["hashed_password"]
    assert result.signup_date == admin_data["signup_date"]
    assert result.other_id == admin_data["other_id"]
    mock_collection.find_one.assert_called_once_with({"_id": ObjectId(admin_id)})


@pytest.mark.asyncio
async def test_get_by_id_invalid_objectid(repo, mock_collection):
    invalid_id = "not_a_valid_objectid"
    result = await repo.get_by_id(invalid_id)
    assert result is None
    mock_collection.find_one.assert_not_called()


@pytest.mark.asyncio
async def test_get_by_id_not_found(repo, mock_collection):
    admin_id = str(ObjectId())
    mock_collection.find_one.return_value = None
    result = await repo.get_by_id(admin_id)
    assert result is None
    mock_collection.find_one.assert_called_once_with({"_id": ObjectId(admin_id)})


@pytest.mark.asyncio
async def test_get_by_email_success(repo, mock_collection):
    email = "admin@example.com"
    admin_data = {
        "_id": ObjectId(),
        "email": email,
        "hashed_password": "hashed_pw",
        "signup_date": datetime(2024, 1, 1, tzinfo=timezone.utc),
        "other_id": "other123",
    }
    mock_collection.find_one.return_value = admin_data

    result = await repo.get_by_email(email)

    assert isinstance(result, AdminDTA)
    assert result.id == str(admin_data["_id"])
    assert result.email == email
    assert result.hashed_password == admin_data["hashed_password"]
    assert result.signup_date == admin_data["signup_date"]
    assert result.other_id == str(admin_data["other_id"])
    mock_collection.find_one.assert_called_once_with({"email": email})


@pytest.mark.asyncio
async def test_get_by_email_not_found(repo, mock_collection):
    email = "notfound@example.com"
    mock_collection.find_one.return_value = None

    result = await repo.get_by_email(email)

    assert result is None
    mock_collection.find_one.assert_called_once_with({"email": email})
