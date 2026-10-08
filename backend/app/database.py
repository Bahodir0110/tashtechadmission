import os
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

# Convert postgres:// to postgresql:// for SQLAlchemy compatibility
if raw_db_url.startswith("postgres://"):
    raw_db_url = raw_db_url.replace("postgres://", "postgresql://", 1)

# Clean channel_binding if present to prevent libpq parameter issues
clean_db_url = raw_db_url
for cb in ["channel_binding=require&", "&channel_binding=require", "?channel_binding=require"]:
    if cb in clean_db_url:
        clean_db_url = clean_db_url.replace(cb, "")

connect_args = {}
engine_kwargs = {"echo": False}

if clean_db_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False
    engine = create_engine(clean_db_url, connect_args=connect_args, **engine_kwargs)
else:
    # Serverless PostgreSQL settings
    engine_kwargs["pool_pre_ping"] = True
    engine_kwargs["pool_recycle"] = 300
    try:
        engine = create_engine(clean_db_url, connect_args=connect_args, **engine_kwargs)
        with engine.connect() as conn:
            pass
        logger.info("Successfully connected to PostgreSQL using default driver.")
    except Exception as e:
        logger.warning(f"Default PostgreSQL driver error ({e}), trying pg8000 fallback...")
        pg8000_url = clean_db_url.replace("postgresql://", "postgresql+pg8000://", 1)
        engine = create_engine(pg8000_url, connect_args=connect_args, **engine_kwargs)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
