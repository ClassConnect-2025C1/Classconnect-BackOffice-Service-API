from datetime import datetime
from pydantic import BaseModel, Field


class AssignmentCreate(BaseModel):
    course_id: str = Field(..., examples=["CS101"])
    title: str = Field(..., max_length=120)
    description: str | None = None
    due_date: datetime
    max_points: int = Field(100, ge=1)


class AssignmentOut(AssignmentCreate):
    id: str = Field(..., description="Mongo document id")
