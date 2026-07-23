import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    APP_NAME: str = "Grievance Management System"
    DEBUG: bool = True
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Email / SMTP Configuration (optional — fallback to console mock if not set)
    MAIL_USERNAME: Optional[str] = None
    MAIL_PASSWORD: Optional[str] = None
    MAIL_FROM: Optional[str] = None
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_PORT: int = 587

    # Upload directories
    UPLOAD_DIR_IMAGES: str = "uploads/images"
    UPLOAD_DIR_PDF: str = "uploads/pdf"
    UPLOAD_DIR_TEXT: str = "uploads/extracted_text"

    class Config:
        env_file = ".env"


settings = Settings()