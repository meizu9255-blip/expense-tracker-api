from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware # <--- CORS Импорты
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from typing import List
from jose import jwt, JWTError
from . import models, database, schemas, crud, utils

# -------------------------------------------------------------------------
# 1. БАПТАУЛАР (SETTINGS)
# -------------------------------------------------------------------------
SECRET_KEY = "YOUR-ULTRA-SECRET-KEY" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 

# Базаны құру
database.Base.metadata.create_all(bind=database.engine)

# Қосымшаны бастау
app = FastAPI(title="Expense Tracker API")

# -------------------------------------------------------------------------
# 2. CORS БАПТАУЛАРЫ (ЕҢ МАҢЫЗДЫСЫ!)
# Бұл код app = FastAPI() жолынан кейін бірден тұруы керек
# -------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Барлық сайттарға рұқсат (Netlify үшін керек)
    allow_credentials=True,
    allow_methods=["*"],  # GET, POST, PUT, DELETE - бәріне рұқсат
    allow_headers=["*"],
)

# -------------------------------------------------------------------------
# 3. ДЕПЕНДЕНСИЯЛАР
# -------------------------------------------------------------------------
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Токен жарамсыз",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = crud.get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user

# -------------------------------------------------------------------------
# 4. API ЭНДПОЙНТТАРЫ
# -------------------------------------------------------------------------

@app.get("/")
def read_root():
    return {"message": "Server is running!"}

# --- AUTH ---
@app.post("/users/", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_email(db, email=user.email):
        raise HTTPException(status_code=400, detail="Бұл Email тіркелген!")
    return crud.create_user(db=db, user=user)

@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, email=form_data.username)
    if not user or not utils.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Қате Email немесе пароль")
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me/", response_model=schemas.User)
def read_users_me(current_user: schemas.User = Depends(get_current_user)):
    return current_user

# --- CATEGORIES ---
@app.post("/categories/", response_model=schemas.CategoryResponse)
def add_category(category: schemas.CategoryCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    return crud.create_user_category(db, category, current_user.id)

@app.get("/categories/", response_model=List[schemas.CategoryResponse])
def get_categories(db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    return crud.get_user_categories(db, current_user.id)

# --- EXPENSES ---
@app.post("/expenses/", response_model=schemas.ExpenseResponse)
def add_expense(expense: schemas.ExpenseCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    return crud.create_user_expense(db, expense, current_user.id)

@app.get("/expenses/", response_model=List[schemas.ExpenseResponse])
def get_expenses(db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    return crud.get_user_expenses(db, current_user.id)

@app.delete("/expenses/{expense_id}")
def delete_expense(expense_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    deleted_expense = crud.delete_user_expense(db, expense_id, current_user.id)
    if deleted_expense is None:
        raise HTTPException(status_code=404, detail="Not found")
    return {"message": "Deleted"}

# --- INCOMES ---
@app.post("/incomes/", response_model=schemas.IncomeResponse)
def add_income(income: schemas.IncomeCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    return crud.create_user_income(db, income, current_user.id)

@app.get("/incomes/", response_model=List[schemas.IncomeResponse])
def get_incomes(db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    return crud.get_user_incomes(db, current_user.id)

# --- BALANCE & STATS ---
@app.get("/balance/", response_model=schemas.BalanceResponse)
def get_balance(db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    return crud.get_user_balance(db, current_user.id)

@app.get("/statistics/expenses/", response_model=List[schemas.CategoryStats])
def get_expense_stats(db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    return crud.get_expenses_by_category(db, current_user.id)