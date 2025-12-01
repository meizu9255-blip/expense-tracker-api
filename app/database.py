import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Render-дегі құпия сілтемені аламыз
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# 2. Егер компьютерде болсақ (сілтеме жоқ болса), localhost-ты қолданамыз
if not SQLALCHEMY_DATABASE_URL:
    SQLALCHEMY_DATABASE_URL = "postgresql://postgres:1234@localhost/expense_db"

# 🔥 ЕҢ МАҢЫЗДЫ ТҮЗЕТУ: 
# Render беретін 'postgres://' сілтемесін 'postgresql://' деп өзгертеміз
# Әйтпесе сервер "Dialect not found" деп құлайды.
if SQLALCHEMY_DATABASE_URL and SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

# 3. Қосылу
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()