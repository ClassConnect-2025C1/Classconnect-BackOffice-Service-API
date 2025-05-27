"""
FastAPI dependency wrappers that higher-level code can import
without knowing where the Motor client lives.
"""

from motor.motor_asyncio import AsyncIOMotorDatabase

from ..config.config import get_settings
from ..db.client import get_client


def get_db() -> AsyncIOMotorDatabase:
    settings = get_settings()
    return get_client()[settings.mongo_db]
