from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator
import os


class Settings(BaseSettings):
    mongo_uri: str = "mongodb://localhost:27017"
    mongo_db: str = "backoffice_db"
    log_level: str = "INFO"
    host: str = "127.0.0.1"
    port: int = 8000
    url_auth: str = "http://localhost:8000"
    url_users: str = "http://localhost:8001"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    @model_validator(mode="before")
    @classmethod
    def adjust_mongo_uri(cls, values: dict) -> dict:
        docker = os.getenv("DOCKER", "").lower()
        uri = values.get("mongo_uri", "mongodb://localhost:27017")
        if docker == "true":
            values["mongo_uri"] = uri.replace(
                "mongodb://localhost", "mongodb://mongodb"
            )
        return values


@lru_cache
def get_settings() -> Settings:
    return Settings()


if __name__ == "__main__":
    print("✅ URI cargada:", get_settings().mongo_uri)
