from __future__ import annotations

import os
from pathlib import Path
from typing import Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

# Load env from backend/.env (local dev) and repo root .env (compose).
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")
load_dotenv(BASE_DIR.parent / ".env")


def get_database_url() -> str:
    # Prefer a full URL if provided, otherwise build from parts.
    explicit_url = os.getenv("DATABASE_URL")
    if explicit_url:
        return explicit_url

    parts = {
        "POSTGRES_USER": os.getenv("POSTGRES_USER"),
        "POSTGRES_PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        "POSTGRES_DB": os.getenv("POSTGRES_DB"),
        "DB_HOST": os.getenv("DB_HOST"),
        "DB_PORT": os.getenv("DB_PORT", "5432"),
    }

    missing = [key for key, value in parts.items() if not value]
    if missing:
        raise RuntimeError(
            "Missing database env vars: " + ", ".join(missing)
        )

    return (
        "postgresql+psycopg2://"
        f"{parts['POSTGRES_USER']}:{parts['POSTGRES_PASSWORD']}"
        f"@{parts['DB_HOST']}:{parts['DB_PORT']}/{parts['POSTGRES_DB']}"
    )


DATABASE_URL = get_database_url()


class Base(DeclarativeBase):
    pass


# pool_pre_ping checks connections before use to avoid stale DB connections.
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# SessionLocal is a factory for new Session objects.
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
