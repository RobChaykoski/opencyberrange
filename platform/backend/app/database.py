"""
Database connection and session management
"""

from sqlalchemy import create_engine, event, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from app.config import settings
from app.actor import get_actor

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
    pool_size=5,
    max_overflow=10,
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


# Dependency to get database session
def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
