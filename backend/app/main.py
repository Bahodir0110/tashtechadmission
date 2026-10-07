import asyncio
import logging
from contextlib import asynccontextmanager
from typing import List, Optional
from fastapi import FastAPI, Depends, Request, status, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from aiogram.types import Update

from .config import settings
from .database import engine, Base, get_db
from .models import Submission, BotSession, UserQuestion
from .schemas import SubmissionCreate, SubmissionResponse, HealthResponse, AdminLoginRequest
from .telegram_bot import send_to_telegram, get_bot, dp

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

    # Start aiogram background polling if not on serverless
    polling_task = None
    bot_instance = get_bot()
    # Check if running on Vercel
    import os
    is_vercel = bool(os.getenv("VERCEL"))
    
    if bot_instance and not is_vercel:
        logger.info("Starting aiogram dispatcher polling for inline button callbacks...")
        polling_task = asyncio.create_task(
            dp.start_polling(bot_instance, allowed_updates=["message", "callback_query"])
        )

    try:
        yield
    finally:
        if polling_task:
            logger.info("Stopping aiogram polling...")
            polling_task.cancel()
            try:
                await polling_task
            except asyncio.CancelledError:
                pass
        if bot_instance:
            await bot_instance.session.close()

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

@app.post("/api/telegram-webhook")
async def telegram_webhook(request: Request):
    """Webhook endpoint for Vercel serverless to process Telegram button clicks."""
    bot_instance = get_bot()
    if not bot_instance:
        return {"ok": False, "error": "Bot not configured"}
    try:
        data = await request.json()
        update = Update.model_validate(data, context={"bot": bot_instance})
        await dp.feed_update(bot_instance, update)
        return {"ok": True}
    except Exception as e:
        logger.error(f"Error handling Telegram webhook: {e}")
        return {"ok": False, "error": str(e)}

@app.get("/api/set-webhook")
async def set_telegram_webhook(url: Optional[str] = None):
    """Helper to set Telegram webhook to your custom domain."""
    bot_instance = get_bot()
    if not bot_instance:
        return {"ok": False, "error": "Bot not configured"}
    try:
        if not url:
            # Info about current webhook
            info = await bot_instance.get_webhook_info()
            return {"ok": True, "webhook_info": info.model_dump()}
        await bot_instance.set_webhook(url=url.strip())
        return {"ok": True, "message": f"Webhook set to {url}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@app.post("/api/submissions", response_model=SubmissionResponse, status_code=status.HTTP_201_CREATED)
async def create_submission(
    payload: SubmissionCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Receive applicant form submission:
    1. Saves data to database.
    2. Sends formatted instant notification with inline buttons to Telegram group chat.
    3. Returns created submission with delivery status.
    """
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent", "")[:255]

    logger.info(f"Received new submission from '{payload.full_name}' ({payload.phone}) for school '{payload.school}'")

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

    db_submission.telegram_sent = tg_success
    db_submission.telegram_message_id = tg_msg_id
    db_submission.telegram_error = tg_err
    db.commit()
    db.refresh(db_submission)

    return db_submission

from .initial_leads import INITIAL_LEADS

def seed_initial_data(db: Session, force: bool = False):
    try:
        count = db.query(Submission).count()
        if count > 0 and not force:
            return

        for item in INITIAL_LEADS:
            existing = db.query(Submission).filter(Submission.phone == item["phone"]).first()
            if not existing:
                c_at = None
                if item.get("created_at"):
                    try:
                        c_at = datetime.fromisoformat(item["created_at"])
                    except Exception:
                        pass
                cont_at = None
                if item.get("contacted_at"):
                    try:
                        cont_at = datetime.fromisoformat(item["contacted_at"])
                    except Exception:
                        pass

                sub = Submission(
                    id=item.get("id"),
                    full_name=item.get("full_name", ""),
                    phone=item.get("phone", ""),
                    telegram_username=item.get("telegram_username", ""),
                    region=item.get("region", ""),
                    school=item.get("school", ""),
                    question_text=item.get("question_text"),
                    telegram_sent=True,
                    telegram_message_id="",
                    telegram_error=None,
                    status=item.get("status", "Yangi"),
                    is_contacted=bool(item.get("is_contacted", False)),
                    contacted_by=item.get("contacted_by"),
                    contacted_at=cont_at,
                    created_at=c_at or datetime.now(timezone.utc),
                    user_agent=item.get("user_agent", "Telegram Bot")
                )
                db.add(sub)
        db.commit()
        logger.info(f"Loaded initial leads. Current count: {db.query(Submission).count()}")
    except Exception as e:
        logger.warning(f"Initial leads loader error: {e}")

def verify_admin(
    authorization: Optional[str] = Header(None),
    x_admin_token: Optional[str] = Header(None)
):
    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split("Bearer ", 1)[1].strip()
    elif x_admin_token:
        token = x_admin_token.strip()

    if not token or token != settings.ADMIN_SECRET_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Kirish taqiqlangan: login va parol talab qilinadi",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return True

@app.post("/api/admin/login")
def admin_login(payload: AdminLoginRequest):
    """Verify admin login credentials and return session token."""
    if (payload.username.strip() == settings.ADMIN_USERNAME and 
        payload.password.strip() == settings.ADMIN_PASSWORD):
        return {
            "ok": True,
            "token": settings.ADMIN_SECRET_TOKEN,
            "username": payload.username.strip()
        }
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Login yoki parol noto'g'ri!"
    )

@app.post("/api/admin/restore-leads")
def restore_leads(
    db: Session = Depends(get_db),
    auth: bool = Depends(verify_admin)
):
    """Restore the 9 actual student leads into the database (Protected)."""
    seed_initial_data(db, force=True)
    subs = db.query(Submission).order_by(Submission.id.desc()).all()
    return {"ok": True, "count": len(subs)}

@app.get("/api/submissions", response_model=List[SubmissionResponse])
def get_submissions(
    skip: int = 0, 
    limit: int = 10000, 
    db: Session = Depends(get_db),
    auth: bool = Depends(verify_admin)
):
    """Retrieve list of submissions ordered by newest first (Protected)."""
    seed_initial_data(db, force=False)
    submissions = (
        db.query(Submission)
        .order_by(Submission.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return submissions

@app.delete("/api/submissions/{submission_id}", status_code=status.HTTP_200_OK)
def delete_submission(
    submission_id: int, 
    db: Session = Depends(get_db),
    auth: bool = Depends(verify_admin)
):
    """Delete a single submission by ID to remove clutter/test entries (Protected)."""
    sub = db.query(Submission).filter(Submission.id == submission_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Ariza topilmadi")
    db.delete(sub)
    db.commit()
    return {"ok": True, "deleted_id": submission_id}

@app.post("/api/submissions/bulk-delete")
async def bulk_delete_submissions(
    request: Request, 
    db: Session = Depends(get_db),
    auth: bool = Depends(verify_admin)
):
    """Delete multiple submissions at once (Protected)."""
    try:
        body = await request.json()
        ids = body.get("ids", [])
        if not ids:
            return {"ok": True, "deleted_count": 0}
        deleted = db.query(Submission).filter(Submission.id.in_(ids)).delete(synchronize_session=False)
        db.commit()
        return {"ok": True, "deleted_count": deleted}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

