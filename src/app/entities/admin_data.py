from pydantic import BaseModel, EmailStr
from datetime import datetime


class AdminDTA(BaseModel):
    id: str
    email: EmailStr
    hashed_password: str
    signup_date: datetime
    other_id: str
