import pytest
from datetime import datetime, timezone
from bson import ObjectId
from pydantic import ValidationError
from src.app.models.log_model import ActionEnum, LogAction


def test_action_enum_values():
    assert ActionEnum.block == "block"
    assert ActionEnum.unblock == "unblock"
    assert ActionEnum.student == "student"
    assert ActionEnum.teacher == "teacher"


def test_log_action_creation_and_serialization():
    user_id = ""
    log_id = ObjectId()
    action = ActionEnum.block
    log_action = LogAction(_id=log_id, action=action, user_id=user_id)
    assert log_action.id == log_id
    assert log_action.action == action
    assert log_action.user_id == user_id
    assert isinstance(log_action.timestamp, datetime)
    assert log_action.timestamp.tzinfo == timezone.utc

    # Test serialization
    serialized = log_action.model_dump(by_alias=True)
    assert serialized["_id"] == str(log_id)
    assert serialized["user_id"] == str(user_id)
    assert serialized["action"] == "block"


def test_log_action_default_id():
    user_id = ""
    log_action = LogAction(action=ActionEnum.teacher, user_id=user_id)
    assert log_action.id is None
    serialized = log_action.model_dump(by_alias=True)
    assert serialized["_id"] is None


def test_log_action_invalid_action():
    user_id = ObjectId()
    with pytest.raises(ValidationError):
        LogAction(action="invalid", user_id=user_id)  # type: ignore


def test_log_action_missing_user_id():
    with pytest.raises(ValidationError):
        LogAction(action=ActionEnum.student, user_id=None)  # type: ignore
