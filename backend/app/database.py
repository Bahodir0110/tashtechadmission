import os
import re
import ssl
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from .config import settings

logger = logging.getLogger("tashtech.database")

raw_db_url = (
    os.environ.get("POSTGRES_URL")
    or os.environ.get("DATABASE_URL")
    or settings.DATABASE_URL
)

engine = None

if raw_db_url and ("postgres" in raw_db_url):
    try:
        # Prepare pure-Python pg8000 connection
        pg_url = raw_db_url
        if pg_url.startswith("postgres://"):
            pg_url = pg_url.replace("postgres://", "postgresql+pg8000://", 1)
        elif pg_url.startswith("postgresql://"):
            pg_url = pg_url.replace("postgresql://", "postgresql+pg8000://", 1)

        # Remove libpq parameters that pg8000 doesn't accept in query string
        clean_pg_url = re.sub(r'[?&](sslmode|channel_binding)=[^&]*', '', pg_url).rstrip('?&')

        ssl_ctx = ssl.create_default_context()
        engine = create_engine(
            clean_pg_url,
            connect_args={"ssl_context": ssl_ctx},
            pool_pre_ping=True,
            pool_recycle=300
        )
        with engine.connect() as conn:
            pass
        logger.info("Successfully connected to Neon PostgreSQL via pg8000.")
    except Exception as e:
        logger.error(f"PostgreSQL connection error: {e}. Falling back to SQLite.")
        engine = None

if engine is None:
    sqlite_url = (
        "sqlite:////tmp/tashtech_submissions.db" 
        if os.environ.get("VERCEL") 
        else "sqlite:///./tashtech_submissions.db"
    )
    engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})
    logger.info("Using SQLite database.")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
