from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# СІЗДІҢ RENDER-ДЕГІ БАЗАҢЫЗДЫҢ СІЛТЕМЕСІ:
SQLALCHEMY_DATABASE_URL = "postgresql://my_expense_db_sgju_user:HhYILFphEXU3WmwaqYIjb0XKW7FqVJqR@dpg-d4k2a7npm1nc73acq0n0-a.frankfurt-postgres.render.com/my_expense_db_sgju"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()