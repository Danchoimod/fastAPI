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

    # SMTP Settings
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str
    SMTP_PASSWORD: str

    # GCS Settings
    # Ưu tiên dùng GCS_CREDENTIALS_JSON (chuỗi JSON) cho Cloud Run
    # Hoặc GCS_CREDENTIALS_FILE (đường dẫn file) cho local / docker-compose
    GCS_CREDENTIALS_FILE: str = ""
    GCS_CREDENTIALS_JSON: str = ""
    GCS_BUCKET_NAME: str

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

    @field_validator("GEMINI_API_KEY", mode="before")
    @classmethod
    def clean_api_key(cls, value):
        if isinstance(value, str):
            return value.strip("'\" ")
        return value

    class Config:
        env_file = ".env"

settings = Settings()
