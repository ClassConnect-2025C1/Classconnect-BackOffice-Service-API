import pytest
from unittest.mock import AsyncMock, MagicMock
from bson import ObjectId
from datetime import datetime, timezone
from src.app.repositories.logs_repository import LogRepository


@pytest.mark.asyncio
async def test_create_inserts_log_and_returns_log_info():
    # Setup
    fake_db = MagicMock()
    fake_collection = AsyncMock()
    fake_db.__getitem__.return_value = fake_collection

    repo = LogRepository(fake_db)
    user_id = str(ObjectId())
    action = "test_action"
    fake_inserted_id = ObjectId()
    fake_collection.insert_one.return_value = AsyncMock(inserted_id=fake_inserted_id)

    # Act
    result = await repo.create_log(user_id, action)

    # Verificaciones
    fake_collection.insert_one.assert_awaited_once()
    called_args = fake_collection.insert_one.call_args[0][0]
    assert called_args["user_id"] == ObjectId(user_id)
    assert called_args["action"] == action
    assert isinstance(called_args["timestamp"], datetime)
    assert called_args["timestamp"].tzinfo == timezone.utc
    assert result["_id"] == fake_inserted_id
    assert result["user_id"] == ObjectId(user_id)
    assert result["action"] == action
    assert isinstance(result["timestamp"], datetime)
