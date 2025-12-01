import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Render-дің өз базасын іздейміз
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# 2. Егер Render-де болмасақ (Компьютерде болсақ), localhost-ты қолданамыз
if not SQLALCHEMY_DATABASE_URL:
    # Егер сіз PostgreSQL қолдансаңыз:
    SQLALCHEMY_DATABASE_URL = "postgresql://postgres:1234@localhost/expense_db"
    # Егер SQLite қолдансаңыз:
    # SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

# 3. Render-дегі қатені түзеу (postgres:// -> postgresql://)
if SQLALCHEMY_DATABASE_URL and SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

# 4. Қосылу
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()