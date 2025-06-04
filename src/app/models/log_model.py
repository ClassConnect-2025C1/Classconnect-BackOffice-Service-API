from datetime import datetime, timezone
from pydantic import BaseModel, Field, ConfigDict, field_serializer
from bson import ObjectId
from enum import Enum


class ActionEnum(str, Enum):
    block = "block"
    unblock = "unblock"
    student = "student"
    teacher = "teacher"


class LogAction(BaseModel):
    id: ObjectId | None = Field(default=None, alias="_id")
    action: ActionEnum
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    user_id: str

    model_config = ConfigDict(validate_by_name=True, arbitrary_types_allowed=True)

    @field_serializer("id", "user_id")
    def serialize_object_id(self, value: ObjectId | None):
        return str(value) if value is not None else None
