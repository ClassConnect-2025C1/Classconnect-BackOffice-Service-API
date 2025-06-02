from pydantic import BaseModel, EmailStr
from datetime import datetime


class AdminDTA(BaseModel):
    id: str
    email: EmailStr
    hashed_password: str
    signup_date: datetime
    other_id: str

    @classmethod
    def from_mongo(cls, data: dict) -> "AdminDTA":
        return cls(
            id=str(data["_id"]),
            email=data["email"],
            hashed_password=data["hashed_password"],
            signup_date=data["signup_date"],
            other_id=str(data["other_id"]),
        )


class User(BaseModel):
    id: str
    email: EmailStr
