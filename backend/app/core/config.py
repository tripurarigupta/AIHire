from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]

class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # --- LLM (AI mock interview) ---
    # Opt-in: with LLM_ENABLED=false the interview feature behaves exactly as
    # it does today, falling back to the rule-based engine in utils/.
    LLM_ENABLED: bool = False
    LLM_PROVIDER: str = "google_genai"
    # Measured on the Gemini free tier: the "lite" Flash model generated a
    # 5-question interview in ~6s versus ~22s for the full Flash model, so it
    # is the default here. Google also restricts access to the 2.5 models for
    # accounts that have not used them before.
    # Note: this model ignores `temperature`, so the value below is not applied.
    LLM_MODEL: str = "gemini-3.5-flash-lite"
    LLM_API_KEY: str = ""
    LLM_TIMEOUT_SECONDS: float = 25.0
    LLM_MAX_RETRIES: int = 2
    LLM_MAX_QUESTIONS: int = 8

    # --- CORS ---
    # Comma-separated extra browser origins allowed to call the API, e.g. a
    # custom frontend domain. Vercel preview deployments get a new hostname per
    # deployment and are matched by regex in app/main.py instead.
    CORS_EXTRA_ORIGINS: str = ""

    model_config = SettingsConfigDict(
        env_file= BASE_DIR/ ".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()