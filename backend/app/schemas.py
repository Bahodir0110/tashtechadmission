from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime

class SubmissionCreate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=255, description="Full Name (F.I.Sh / Ф.И.О)")
    phone: str = Field(..., min_length=7, max_length=50, description="Phone number")
    telegram_username: str = Field(..., min_length=2, max_length=100, description="Telegram User Name")
    region: str = Field(..., min_length=2, max_length=100, description="Selected region")
    school: str = Field(..., min_length=2, max_length=255, description="School/Lyceum where applicant studies")
    question_text: Optional[str] = Field(None, max_length=2000, description="Optional question or comment")

    @field_validator("telegram_username")
    @classmethod
    def format_telegram_username(cls, v: str) -> str:
        clean = v.strip()
        if not clean.startswith("@"):
            clean = f"@{clean}"
        return clean

    @field_validator("full_name")
    @classmethod
    def clean_name(cls, v: str) -> str:
        clean = v.strip()
        if len(clean) < 2:
            raise ValueError("Name is too short")
        return clean

class SubmissionResponse(BaseModel):
    id: int
    full_name: str
    phone: str
    telegram_username: str
    region: str
    school: str
    question_text: Optional[str] = None
    telegram_sent: bool
    status: Optional[str] = "Yangi"
    is_contacted: bool = False
    contacted_by: Optional[str] = None
    contacted_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

class HealthResponse(BaseModel):
    status: str
    project: str
    telegram_configured: bool
    db_connected: bool
