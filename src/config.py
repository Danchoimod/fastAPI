from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Project"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True

    class Config:
        env_file = ".env"

settings = Settings()
