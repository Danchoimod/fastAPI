from pydantic_settings import BaseSettings
from pydantic import field_validator

class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Project"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True
    MONGODB_URL: str
    MONGODB_DB_NAME: str

    # JWT Authentication Settings
    JWT_SECRET_KEY: str
    JWT_REFRESH_SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Gemini AI API Settings
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-3.1-flash-lite-preview"

    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug(cls, value):
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"release", "production", "prod"}:
                return False
            if normalized in {"debug", "development", "dev"}:
                return True

        return value

    class Config:
        env_file = ".env"

settings = Settings()
