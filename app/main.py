from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from typing import List, Optional
from jose import jwt, JWTError
from pydantic import BaseModel
from . import models, database, schemas, crud, utils


# --- КОНСТАНТАЛАР (ӨЗГЕРТПЕҢІЗ) ---
SECRET_KEY = "YOUR-ULTRA-SECRET-KEY"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()

database.Base.metadata.create_all(bind=database.engine) 



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- DEPENDENCIES ---
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# --- АУТЕНТИФИКАЦИЯ ЖӘНЕ ТОКЕН ФУНКЦИЯЛАРЫ ---
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None: raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError: raise HTTPException(status_code=401, detail="Invalid token")
    user = crud.get_user_by_email(db, email=email)
    if user is None: raise HTTPException(status_code=401, detail="User not found")
    return user


# --- АУТЕНТИФИКАЦИЯ (ТІРКЕЛУ/КІРУ) ---
@app.post("/users/", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_email(db, email=user.email):
        raise HTTPException(status_code=400, detail="Бұл email тіркелген!")
    return crud.create_user(db=db, user=user)

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, email=form_data.username)
    if not user or not utils.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Қате email немесе құпия сөз")
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me/", response_model=schemas.User)
def read_users_me(current_user: schemas.User = Depends(get_current_user)):
    return current_user


# --- КАТЕГОРИЯЛАР (Басқару) ---
@app.post("/categories/", response_model=schemas.CategoryResponse)
def add_category(category: schemas.CategoryCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    return crud.create_user_category(db, category, current_user.id)

@app.get("/categories/", response_model=List[schemas.CategoryResponse])
def get_categories(db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    return crud.get_user_categories(db, current_user.id)


# --- ШЫҒЫНДАР (EXPENSES) ---
@app.post("/expenses/", response_model=schemas.ExpenseResponse)
def add_expense(expense: schemas.ExpenseCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    return crud.create_user_expense(db, expense, current_user.id)

@app.get("/expenses/", response_model=List[schemas.ExpenseResponse])
def get_expenses(db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    return crud.get_user_expenses(db, current_user.id)

@app.delete("/expenses/{expense_id}")
def delete_expense(expense_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    crud.delete_user_expense(db, expense_id, current_user.id)
    return {"message": "Сәтті өшірілді"}


# --- КІРІСТЕР (INCOMES) ---
@app.post("/incomes/", response_model=schemas.IncomeResponse)
def add_income(income: schemas.IncomeCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    return crud.create_user_income(db, income, current_user.id)

@app.get("/incomes/", response_model=List[schemas.IncomeResponse])
def get_incomes(db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    return crud.get_user_incomes(db, current_user.id)


# --- БАЛАНС ЖӘНЕ СТАТИСТИКА ---
@app.get("/balance/", response_model=schemas.BalanceResponse)
def get_balance(db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    return crud.get_user_balance(db, current_user.id)

@app.get("/statistics/expenses/", response_model=List[schemas.CategoryStats])
def get_stats(db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    return crud.get_expenses_by_category(db, current_user.id)


# --- БЮДЖЕТ API ---
@app.post("/budgets/", response_model=schemas.BudgetResponse)
def create_budget(budget: schemas.BudgetCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    return crud.create_budget(db=db, budget=budget, user_id=current_user.id)

@app.get("/budgets/", response_model=List[schemas.BudgetResponse])
def read_budgets(db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    return crud.get_user_budgets(db, user_id=current_user.id)

class UserUpdate(BaseModel):
    username: Optional[str] = None 
    email: Optional[str] = None

class UserPasswordUpdate(BaseModel):
    old_password: str
    new_password: str

@app.put("/users/me")
def update_user_profile(
    user_data: UserUpdate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    if user_data.email and user_data.email != current_user.email:
        existing_user = crud.get_user_by_email(db, email=user_data.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Бұл email бос емес!")
        current_user.email = user_data.email
    
    if user_data.username and hasattr(current_user, "username"):
        current_user.username = user_data.username
    
    try:
        db.commit()
        db.refresh(current_user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Сақтау кезінде қате шықты")
        
    return current_user

@app.put("/users/password")
def change_user_password(
    pass_data: UserPasswordUpdate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    if not utils.verify_password(pass_data.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Ескі құпия сөз қате!")

    current_user.hashed_password = utils.get_password_hash(pass_data.new_password)
    db.commit()
    
    return {"message": "Құпия сөз сәтті өзгертілді!"}

@app.delete("/users/me")
def delete_user_me(
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    try:
        db.delete(current_user)
        db.commit()
        return {"message": "Аккаунт және барлық деректер сәтті өшірілді!"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Өшіру кезінде қате шықты")
