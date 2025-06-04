from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection

REPOSITORY = "logs"


class LogRepository:
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.collection: AsyncIOMotorCollection = db[REPOSITORY]

    async def create_log(self, user_id: str, action: str):
        log_info = {
            "user_id": user_id,
            "action": action,
            "timestamp": datetime.now(timezone.utc),
        }
        result = await self.collection.insert_one(log_info)
        log_info["_id"] = result.inserted_id
        return log_info
