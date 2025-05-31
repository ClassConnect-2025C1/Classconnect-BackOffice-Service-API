from datetime import datetime, timezone
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_serializer
from bson import ObjectId


class Admin(BaseModel):
    id: ObjectId | None = Field(default=None, alias="_id")
    email: EmailStr
    hashed_password: str
    signup_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    other_id: ObjectId | None = None

    model_config = ConfigDict(validate_by_name=True, arbitrary_types_allowed=True)

    @field_serializer("id", "other_id")
    def serialize_object_id(self, value: ObjectId | None):
        return str(value) if value is not None else None
