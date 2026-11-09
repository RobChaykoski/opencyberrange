"""
Database connection and session management
"""

import logging
import os
import time
from functools import wraps

from sqlalchemy import create_engine, event, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from app.config import settings
from app.actor import get_actor

logger = logging.getLogger(__name__)

# Per-process pool sizing. The total connection ceiling is
# (DB_POOL_SIZE + DB_MAX_OVERFLOW) * uvicorn workers. Keep that below the
# PostgreSQL max_connections minus reserved slots: a 9-worker deployment with
# the old 5 + 10 defaults could ask for 135 connections against a 100 limit.
# The 4 + 4 defaults put 9 workers at 72 connections, leaving room for the
# scheduler, migrations, and an operator session.
_pool_size = max(1, int(os.environ.get("DB_POOL_SIZE", "4")))
_max_overflow = max(0, int(os.environ.get("DB_MAX_OVERFLOW", "4")))

_connect_args = {}
if settings.DATABASE_URL.startswith("postgresql"):
    # The integrity trigger uses application_name as a fallback when no
    # authenticated actor context is set: ocr-app => system, anything else =>
    # unattributed (manual client).
    _connect_args["application_name"] = "ocr-app"

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=_pool_size,
    max_overflow=_max_overflow,
    pool_recycle=300,
    pool_timeout=30,
    # Reuse the hottest connection first. Under bursty request patterns this
    # lets the colder half of the pool age out via pool_recycle instead of
    # every worker keeping all 15 slots open to PostgreSQL.
    pool_use_lifo=True,
    connect_args=_connect_args,
)

# SQLite is used by the local test suite. Enforce foreign keys there so
# ON DELETE CASCADE behaves like PostgreSQL; without this, deleted users can
# leave orphan achievements and survey events behind between tests.
if engine.dialect.name == "sqlite":
    from sqlalchemy import event

    @event.listens_for(engine, "connect")
    def _enable_sqlite_foreign_keys(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


if engine.dialect.name == "postgresql":
    @event.listens_for(Session, "before_flush")
    def _stamp_actor_context(session, flush_context, instances):
        """Set the request actor for the integrity trigger before a flush.

        SET LOCAL is scoped to the current transaction, so it is re-applied on
        every flush. A system job with no actor falls back to application_name
        inside the trigger.
        """
        if session.bind is None or session.bind.dialect.name != "postgresql":
            return
        actor = get_actor()
        if not (actor.actor_type or actor.actor_id or actor.request_id):
            return
        session.connection().execute(
            text(
                "SELECT set_config('ocr.actor_type', :actor_type, true), "
                "set_config('ocr.actor_id', :actor_id, true), "
                "set_config('ocr.request_id', :request_id, true)"
            ),
            {
                "actor_type": actor.actor_type or "",
                "actor_id": "" if actor.actor_id is None else str(actor.actor_id),
                "request_id": actor.request_id or "",
            },
        )


def _deadlock_code(exc: OperationalError) -> str | None:
    """PostgreSQL SQLSTATE for a deadlock or serialization failure."""
    orig = getattr(exc, "orig", None)
    return (
        getattr(orig, "pgcode", None)
        or getattr(getattr(orig, "diag", None), "sqlstate", None)
    )


def retry_on_deadlock(func):
    """Retry a transaction-owning service function on PostgreSQL 40P01/40001.

    The wrapped function must own its transaction (it commits before it
    returns). A deadlock aborts the transaction, so the session is rolled back
    before the retry. Do not apply this to a function that runs inside a larger
    transaction: rolling back would discard the caller's pending writes.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        db = kwargs.get("db")
        if db is None:
            for arg in args:
                if isinstance(arg, Session):
                    db = arg
                    break

        for attempt in range(3):
            try:
                return func(*args, **kwargs)
            except OperationalError as exc:
                code = _deadlock_code(exc)
                if code not in ("40P01", "40001") or attempt == 2:
                    raise
                logger.warning(
                    "Retrying %s after database deadlock (%s), attempt %d/3",
                    func.__name__, code, attempt + 1,
                )
                if db is not None:
                    try:
                        db.rollback()
                    except Exception:
                        pass
                time.sleep(0.05 * (2 ** attempt))
    return wrapper


# Dependency to get database session
def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
