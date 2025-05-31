from pydantic import EmailStr
from datetime import datetime, timezone
from src.app.entities.admin_data import AdminDTA
from pymongo.database import Database
from pymongo.collection import Collection
from bson import ObjectId

REPOSITORY = "admin"


class AdminRepository:
    def __init__(self, db: Database) -> None:
        self.collection: Collection = db[REPOSITORY]

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

    def get_by_id(self, admin_id: str) -> AdminDTA | None:
        try:
            _id = ObjectId(admin_id)
        except Exception:
            return None

        admin_data = self.collection.find_one({"_id": _id})
        if not admin_data:
            return None

        return AdminDTA(
            id=str(admin_data["_id"]),
            email=admin_data["email"],
            hashed_password=admin_data["hashed_password"],
            signup_date=admin_data["signup_date"],
            other_id=str(admin_data["other_id"]),
        )
