from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str

    model_config = SettingsConfigDict(
        env_file= BASE_DIR/ ".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()