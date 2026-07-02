from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Sentinel Doorbell AI"
    environment: str = "development"
    database_url: str = "sqlite:///./doorbell.db"
    media_dir: Path = Path("./media")
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    device_id: str = "front_door_01"
    camera_source: str = "demo://front-door"
    min_confidence: float = 0.65
    event_cooldown_seconds: int = 45
    august_lock_id: str = "front-door-lock"
    agent_mode: str = "mock"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()

