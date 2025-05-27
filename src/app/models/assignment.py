"""
MongoDB representation of an Assignment document.

We keep it thin—just enough to round-trip data in/out of the DB.
If you switch to Beanie/ODMantic later, only this file changes.
"""
from datetime import datetime
from bson import ObjectId
from pydantic import BaseModel, Field, ConfigDict


class AssignmentInDB(BaseModel):
    id: ObjectId | None = Field(default=None, alias="_id")

    course_id: str = Field(..., examples=["CS101"])
    title: str = Field(..., max_length=120)
    description: str | None = None
    due_date: datetime
    max_points: int = 100

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
