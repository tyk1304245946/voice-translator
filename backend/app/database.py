from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from datetime import datetime, timezone
from app.config import settings

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


class HistoryRecord(Base):
    __tablename__ = "history"

    id = Column(Integer, primary_key=True, index=True)
    original_text = Column(Text, nullable=False)
    translated_text = Column(Text, nullable=False)
    audio_filename = Column(String, nullable=True)
    download_name = Column(String, nullable=True)
    mode = Column(String, default="normal")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    _migrate_history_table()


def _migrate_history_table() -> None:
    # 兼容老库：为已有 history 表补上 download_name 列。
    with engine.begin() as conn:
        columns = conn.execute(text("PRAGMA table_info(history)")).fetchall()
        existing = {row[1] for row in columns}
        if "download_name" not in existing:
            conn.execute(text("ALTER TABLE history ADD COLUMN download_name VARCHAR"))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
