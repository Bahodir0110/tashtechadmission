import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "TashTech Onboarding Portal API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    # Telegram Bot Settings
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_CHAT_ID: Optional[str] = None
    
    # Database
    DATABASE_URL: str = (
        os.environ.get("POSTGRES_URL")
        or os.environ.get("DATABASE_URL")
        or (
            "sqlite:////tmp/tashtech_submissions.db" 
            if os.environ.get("VERCEL") 
            else "sqlite:///./tashtech_submissions.db"
        )
    )
    
    # CORS Origins
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173", "http://127.0.0.1:3000", "*"]

    # Admin Credentials for /jadval
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "tashtech2026"
    ADMIN_SECRET_TOKEN: str = "tashtech_admin_token_2026"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

settings = Settings()

