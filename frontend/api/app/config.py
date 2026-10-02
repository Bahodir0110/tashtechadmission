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
        "sqlite:////tmp/tashtech_submissions.db" 
        if os.environ.get("VERCEL") 
        else "sqlite:///./tashtech_submissions.db"
    )
    
    # CORS Origins
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173", "http://127.0.0.1:3000", "*"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

settings = Settings()

