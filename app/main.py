from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from typing import List, Optional
from jose import jwt, JWTError
from pydantic import BaseModel
import requests 
from . import models, database, schemas, crud, utils

# app/models, app/database, app/schemas, app/crud, app/utils модульдерінен импорт
from . import models, database, schemas, crud, utils


# --- КОНСТАНТАЛАР (ӨЗГЕРТПЕҢІЗ) ---
SECRET_KEY = "YOUR-ULTRA-SECRET-KEY" # Өзгерту қажет
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
BOT_TOKEN = "8121209780:AAFM3mQsDDbJRtCOwKpP2D_EPeYNG_P8K4c" # Сіздің Telegram бот токеныңіз


# --- FASTAPI ҚОСЫМШАСЫНЫҢ ИНИЦИАЛИЗАЦИЯСЫ ---
app = FastAPI()

database.Base.metadata.create_all(bind=database.engine)
# 💥 FIX: Қате шығаратын DB инициализациясын алып тастау - ДҰРЫС.
# database.Base.metadata.create_all(bind=database.engine) 


# --- CORS КОНФИГУРАЦИЯСЫ (МАҢЫЗДЫ: Frontend/Backend байланысы) ---
# FIX: allow_origins=["*"] - бұл жергілікті HTML файлын (origin 'null') және Render домендерін қолдануға рұқсат береді.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Барлық домендерден сұранысқа рұқсат
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


# --- ТЕЛЕГРАМ ХАБАРЛАМАСЫН ЖІБЕРУ ФУНКЦИЯСЫ ---
def send_telegram_message(chat_id: str, text: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        # parse_mode=HTML (Болдыру үшін)
        requests.post(url, data={"chat_id": chat_id, "text": text, "parse_mode": "HTML"}) 
    except:
        pass


# =========================================================================
# ⬇️ API ROUTERS (Endpoint) ⬇️
# =========================================================================

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


# --- ҚОЛДАНУШЫ ПРОФИЛІН ЖӘНЕ ҚҰПИЯ СӨЗІН ӨЗГЕРТУ (ПРОФИЛЬ МОДУЛІ) ---
class UserUpdate(BaseModel):
    username: Optional[str] = None # username өрісі міндетті емес
    email: Optional[str] = None # email өрісі міндетті емес

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


# =========================================================================
# ⬇️ ТЕЛЕГРАМ ИНТЕГРАЦИЯСЫ (КӨП ЮЗЕРЛІ ЖҮЙЕ) ⬇️
# =========================================================================

# --- TELEGRAM WEBHOOK (Транзакцияларды қабылдау) ---
@app.post("/webhook")
async def telegram_webhook(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
        
        # Егер бұл хабарлама емес, басқа типтегі жаңарту болса
        if "message" not in data:
            return {"status": "ok"}
            
        chat_id = str(data["message"]["chat"]["id"]) # Telegram Chat ID
        text = data["message"].get("text", "")
        
        # 1. Тіркелген қолданушыны іздеу
        user = db.query(models.User).filter(models.User.telegram_chat_id == chat_id).first()
        
        # 2. Егер қолданушы табылса
        if user:
            # /start командасына жауап
            if text == "/start":
                send_telegram_message(chat_id, f"Сәлем, {user.username}! 👋\nМаған '5000 Обед' деп жазсаң, мен оны сенің шығының қылып тіркеймін.")
                return {"status": "ok"}
                
            # Транзакцияны өңдеу логикасы: 'Сома Сипаттама'
            parts = text.split(" ", 1)
            
            # Соманың дұрыс сандық форматта екенін тексеру
            amount_str = parts[0]
            try:
                # Нүктесі бар санды да қабылдайды
                amount = float(amount_str) 
            except ValueError:
                send_telegram_message(chat_id, "❌ Түсінбедім. Маған <b>'Сома Себеп'</b> деп жаз.\nМысалы: <code>2000 Такси</code>")
                return {"status": "ok"}
                
            description = parts[1] if len(parts) > 1 else "Telegram-нан"
            
            # Санат ID-ін табу немесе әдепкі мәнді қою (Сіздің CRUD-ыңызда 9-шы ID бар деп есептейміз)
            category_id = 9 # "Басқа" шығын санаты
            
            new_expense = schemas.ExpenseCreate(
                amount=amount,
                description=description,
                # DB-ге жазу үшін қазіргі датаны string форматында береміз
                date=datetime.now().strftime("%Y-%m-%d"), 
                category_id=category_id
            )
            
            # Транзакцияны НАҚТЫ ОСЫ ЮЗЕРГЕ жазу
            crud.create_user_expense(db, new_expense, user.id)
            
            send_telegram_message(chat_id, f"✅ <b>Қабылданды!</b>\n➖ {amount} ₸\n📝 {description}")
            
        
        # 3. Егер қолданушы тіркелмесе
        else:
            send_telegram_message(chat_id, 
                "❌ **Аккаунт табылған жоқ.**\n\nСайтта тіркелген аккаунтыңызды жалғау үшін, маған Telegram ID нөміріңізді жіберіңіз.\n\n"
                "<b>ID-ді қалай жалғау керек:</b> \n1. Сайтқа кіріңіз. \n2. Профильді ашыңыз. \n3. 'Telegram ID-ді жалғау' батырмасын басып, ID-іңізді енгізіңіз."
            )
            
    except Exception as e:
        # Қате туындаған кезде жауап беру (webhook-тің қайта жіберуін болдырмау үшін)
        print(f"Webhook Error: {e}")
    
    return {"status": "ok"}

# --- TELEGRAM ID-ді Аккаунтқа жалғау ---
class TelegramLink(BaseModel):
    telegram_chat_id: str
    
@app.put("/users/link_telegram")
def link_telegram_id(
    link_data: TelegramLink, 
    current_user: models.User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    # 1. Чат ID басқа юзерге тіркелген бе, тексереміз
    existing_user = db.query(models.User).filter(models.User.telegram_chat_id == link_data.telegram_chat_id).first()
    
    if existing_user and existing_user.id != current_user.id:
        raise HTTPException(status_code=400, detail="Бұл Telegram ID басқа аккаунтқа тіркелген.")

    # 2. Сақтау
    current_user.telegram_chat_id = link_data.telegram_chat_id
    db.commit()
    db.refresh(current_user)
    
    # 3. Юзерге бот арқылы тексеру хабарламасын жіберу
    send_telegram_message(link_data.telegram_chat_id, 
        f"🥳 <b>Құттықтаймыз, {current_user.username}!</b>\n\nСіздің Qarjy Pro аккаунтыңыз сәтті жалғанды.\nЕнді маған жай ғана '5000 Обед' деп жазсаңыз болады."
    )
    
    return {"message": "Telegram сәтті жалғанды"}