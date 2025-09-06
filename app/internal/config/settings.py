from dotenv import load_dotenv
import os
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    SECRET_KEY: str = "dev-secret"
    DATABASE_URL: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()   