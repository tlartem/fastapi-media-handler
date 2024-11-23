from pydantic_settings import BaseSettings
from sqlalchemy.orm import DeclarativeBase


class Settings(BaseSettings):
    DATABASE_URL: str
    STORAGE_PATH: str
    CLOUD_STORAGE_URL: str

    CHUNK_SIZE: int = 1024 * 1024
    READ_CHUNK_SIZE: int = 10 * 1024 * 1024  # 10 Mb

    AWS_S3_REGION_NAME: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_ACCESS_KEY_ID: str
    AWS_S3_ENDPOINT_URL: str
    BACKET_NAME: str

    class Config:
        env_file = ".env"


settings = Settings()


class Base(DeclarativeBase):
    pass
