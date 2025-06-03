from pydantic import EmailStr
from datetime import datetime, timezone
from src.app.entities.admin_entity import AdminDTA
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from bson import ObjectId

REPOSITORY = "logs"


class LogRepository:
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.collection: AsyncIOMotorCollection = db[REPOSITORY]

    async def create_log(self, user_id: str, action: str):
        log_info = {
            "user_id": ObjectId(user_id),
            "action": action,
            "timestamp": datetime.now(timezone.utc),
        }
        result = await self.collection.insert_one(log_info)
        log_info["_id"] = result.inserted_id
        return log_info
