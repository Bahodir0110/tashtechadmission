from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from datetime import datetime, timezone
from .database import Base

class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=False)
    telegram_username = Column(String(100), nullable=False)
    region = Column(String(100), nullable=False)
    school = Column(String(255), nullable=False)
    question_text = Column(Text, nullable=True)
    
    # Telegram tracking
    telegram_sent = Column(Boolean, default=False)
    telegram_message_id = Column(String(100), nullable=True)
    telegram_error = Column(Text, nullable=True)

    # Status tracking ("Yangi", "Aloqaga chiqildi", "Telefon ko'tarilmadi", "Bekor qildi")
    status = Column(String(50), default="Yangi")
    is_contacted = Column(Boolean, default=False)
    contacted_by = Column(String(100), nullable=True)
    contacted_at = Column(DateTime, nullable=True)
    
    # Metadata
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<Submission(id={self.id}, name='{self.full_name}', status='{self.status}')>"

class BotSession(Base):
    __tablename__ = "bot_sessions"

    user_id = Column(String(50), primary_key=True, index=True)
    step = Column(String(50), default="IDLE")  # "NAME", "PHONE", "TG", "REGION", "SCHOOL", "QUESTION", "ASK_QUESTION"
    data = Column(Text, default="{}")          # JSON string
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class UserQuestion(Base):
    __tablename__ = "user_questions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String(50), nullable=False, index=True)
    username = Column(String(100), nullable=True)
    full_name = Column(String(255), nullable=True)
    question_text = Column(Text, nullable=False)
    group_message_id = Column(Integer, nullable=True, index=True)
    is_answered = Column(Boolean, default=False)
    answer_text = Column(Text, nullable=True)
    answered_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

