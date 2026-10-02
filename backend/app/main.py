from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import logging
from contextlib import asynccontextmanager

from .config import settings
from .database import engine, Base, get_db
from .models import Submission
from .schemas import SubmissionCreate, SubmissionResponse, HealthResponse
from .telegram_bot import send_to_telegram

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("tashtech.api")

# Ensure database tables exist
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized successfully.")
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health", response_model=HealthResponse)
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint to verify database and Telegram bot configuration."""
    db_ok = False
    try:
        db.execute(Submission.__table__.select().limit(1))
        db_ok = True
    except Exception:
        db_ok = False

    tg_configured = bool(
        settings.TELEGRAM_BOT_TOKEN 
        and settings.TELEGRAM_CHAT_ID 
        and "YOUR_" not in settings.TELEGRAM_BOT_TOKEN
    )

    return HealthResponse(
        status="healthy" if db_ok else "degraded",
        project=settings.PROJECT_NAME,
        telegram_configured=tg_configured,
        db_connected=db_ok
    )

@app.post("/api/submissions", response_model=SubmissionResponse, status_code=status.HTTP_201_CREATED)
async def create_submission(
    payload: SubmissionCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Receive applicant form submission:
    1. Saves data to local SQLite database.
    2. Sends formatted instant notification to Telegram group chat via aiogram.
    3. Returns created submission with delivery status.
    """
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent", "")[:255]

    logger.info(f"Received new submission from '{payload.full_name}' ({payload.phone}) for school '{payload.school}'")

    # 1. Create DB record
    db_submission = Submission(
        full_name=payload.full_name.strip(),
        phone=payload.phone.strip(),
        telegram_username=payload.telegram_username.strip(),
        region=payload.region.strip(),
        school=payload.school.strip(),
        question_text=payload.question_text.strip() if payload.question_text else None,
        ip_address=client_ip,
        user_agent=user_agent
    )
    db.add(db_submission)
    db.commit()
    db.refresh(db_submission)

    # 2. Dispatch to Telegram with aiogram
    tg_success, tg_msg_id, tg_err = await send_to_telegram(
        submission_id=db_submission.id,
        full_name=db_submission.full_name,
        phone=db_submission.phone,
        telegram_username=db_submission.telegram_username,
        region=db_submission.region,
        school=db_submission.school,
        question_text=db_submission.question_text,
        created_at=db_submission.created_at
    )

    # 3. Update DB record with Telegram dispatch status
    db_submission.telegram_sent = tg_success
    db_submission.telegram_message_id = tg_msg_id
    db_submission.telegram_error = tg_err
    db.commit()
    db.refresh(db_submission)

    return db_submission

@app.get("/api/submissions", response_model=List[SubmissionResponse])
def get_submissions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieve list of submissions ordered by newest first."""
    submissions = (
        db.query(Submission)
        .order_by(Submission.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return submissions
