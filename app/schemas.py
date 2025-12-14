from pydantic import BaseModel, EmailStr, Field 
from typing import Optional, List
from datetime import date

# ----------------------------------------------------
# 1. USER (Қолданушы)
# ----------------------------------------------------
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    # ВАЛИДАЦИЯ: Пароль кемінде 4 символ болуы керек
    password: str = Field(..., min_length=4) 

class User(UserBase):
    id: int
    is_active: bool
    class Config:
        from_attributes = True

# ----------------------------------------------------
# 2. CATEGORY (Санаттар)
# ----------------------------------------------------
class CategoryCreate(BaseModel):
    name: str

class CategoryResponse(CategoryCreate):
    id: int
    user_id: int
    class Config:
        from_attributes = True

# ----------------------------------------------------
# 3. EXPENSE (Шығын)
# ----------------------------------------------------
class ExpenseBase(BaseModel):
    # ВАЛИДАЦИЯ: Сома 0-ден үлкен болуы керек (gt = greater than)
    amount: float = Field(..., gt=0) 
    description: Optional[str] = None
    category_id: int 
    date: date 

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseResponse(ExpenseBase):
    id: int
    date: date 
    user_id: int
    class Config:
        from_attributes = True

# ----------------------------------------------------
# 4. INCOME (Кіріс)
# ----------------------------------------------------
class IncomeBase(BaseModel):
    # ВАЛИДАЦИЯ: Сома 0-ден үлкен болуы керек
    amount: float = Field(..., gt=0)
    description: Optional[str] = None
    category_id: Optional[int] = None
    
class IncomeCreate(IncomeBase):
    date: date

class IncomeResponse(IncomeBase):
    id: int
    date: date 
    user_id: int
    class Config:
        from_attributes = True

# ----------------------------------------------------
# 5. BUDGET (Бюджет)
# ----------------------------------------------------
class BudgetBase(BaseModel):
    # ВАЛИДАЦИЯ: Лимит те оң сан болуы керек
    limit_amount: float = Field(..., gt=0)
    category_id: int
    start_date: date
    end_date: date

class BudgetCreate(BudgetBase):
    pass

class BudgetResponse(BudgetBase):
    id: int
    user_id: int
    class Config:
        from_attributes = True

# ----------------------------------------------------
# 6. EXPENSE UPDATE
# ----------------------------------------------------
class ExpenseUpdate(BaseModel):
    amount: Optional[float] = Field(None, gt=0) # Өзгерткенде де тексереміз
    description: Optional[str] = None
    category_id: Optional[int] = None
    date: Optional[date] = None

# ----------------------------------------------------
# 7. BALANCE & STATS
# ----------------------------------------------------
class BalanceResponse(BaseModel):
    total_income: float
    total_expenses: float
    net_balance: float

class CategoryStats(BaseModel):
    category_name: str
    total_amount: float

from pydantic import BaseModel

class TelegramLink(BaseModel):
    telegram_chat_id: str