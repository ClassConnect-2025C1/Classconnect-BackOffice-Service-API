from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from src.app.config.config import get_settings

_settings = get_settings()
_client: AsyncIOMotorClient | None = None


def get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(_settings.mongo_uri)
    return _client


def get_db() -> AsyncIOMotorDatabase:
    return get_client()[_settings.mongo_db]
