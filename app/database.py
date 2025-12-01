import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Егер Render-де болсақ, оның өз базасын аламыз.
# Егер компьютерде болсақ, сіздің localhost-ты аламыз.
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

if not SQLALCHEMY_DATABASE_URL:
    # Компьютер үшін (Localhost)
    SQLALCHEMY_DATABASE_URL = "postgresql://postgres:1234@localhost/expense_db"
else:
    # Render үшін (postgres:// -> postgresql:// түзетуімен)
    if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

# 2. Қосылу
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()