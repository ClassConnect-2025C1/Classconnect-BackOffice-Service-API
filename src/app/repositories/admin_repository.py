from pydantic import EmailStr
from datetime import datetime, timezone
from src.app.entities.admin_data import AdminDTA
from pymongo.database import Database

REPOSITORY = "admin"


class AdminRepository:
    def __init__(self, db: Database) -> None:
        self.collection = db[REPOSITORY]

    def create(self, email: EmailStr, hashed_password: str, other_id: str) -> AdminDTA:
        admin_data = {
            "email": email,
            "hashed_password": hashed_password,
            "signup_date": datetime.now(timezone.utc),
            "other_id": other_id,
        }
        result = self.collection.insert_one(admin_data)

        return AdminDTA(
            id=str(result.inserted_id),
            email=email,
            hashed_password=hashed_password,
            signup_date=admin_data["signup_date"],
            other_id=other_id,
        )
