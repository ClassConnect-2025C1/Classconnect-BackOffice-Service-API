from pydantic import EmailStr
from datetime import datetime, timezone
from src.app.entities.admin_entity import AdminDTA
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from bson import ObjectId

REPOSITORY = "admin"


class AdminRepository:
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.collection: AsyncIOMotorCollection = db[REPOSITORY]

    async def create(
        self, email: EmailStr, hashed_password: str, other_id: str
    ) -> AdminDTA:
        admin_data = {
            "email": email,
            "hashed_password": hashed_password,
            "signup_date": datetime.now(timezone.utc),
            "other_id": other_id,
        }
        result = await self.collection.insert_one(admin_data)
        admin_data["_id"] = result.inserted_id
        return AdminDTA.from_mongo(admin_data)

    async def get_by_id(self, admin_id: str) -> AdminDTA | None:
        try:
            _id = ObjectId(admin_id)
        except Exception:
            return None

        admin_data = await self.collection.find_one({"_id": _id})
        if not admin_data:
            return None
        return AdminDTA.from_mongo(admin_data)

    async def get_by_email(self, email: EmailStr) -> AdminDTA | None:
        admin_data = await self.collection.find_one({"email": email})
        if not admin_data:
            return None
        return AdminDTA.from_mongo(admin_data)
