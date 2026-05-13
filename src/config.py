from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Project"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True
    MONGODB_URL: str
    MONGODB_DB_NAME: str

    class Config:
        env_file = ".env"

settings = Settings()
