from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date 

# ----------------------------------------------------
# 1. USER (Пользователь) СХЕМА
# ----------------------------------------------------
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str 

class User(UserBase):
    id: int
    is_active: bool
    
    class Config:
        from_attributes = True

# ----------------------------------------------------
# 2. CATEGORY (Категория) СХЕМА
# ----------------------------------------------------
class CategoryCreate(BaseModel):
    name: str

class CategoryResponse(CategoryCreate):
    id: int
    user_id: int
    class Config:
        from_attributes = True

# ----------------------------------------------------
# 3. EXPENSE (Расход) СХЕМА
# ----------------------------------------------------
class ExpenseBase(BaseModel):
    amount: float
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
# 4. INCOME (Доход/Платеж) СХЕМА
# ----------------------------------------------------
class IncomeBase(BaseModel):
    amount: float
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
# 5. BUDGET (Бюджет) СХЕМА
# ----------------------------------------------------
class BudgetBase(BaseModel):
    limit_amount: float
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
# 6. EXPENSE UPDATE (Обновление) СХЕМА
# ----------------------------------------------------
class ExpenseUpdate(BaseModel):
    amount: Optional[float] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    # ЭТА СТРОКА: Убедитесь, что здесь только обычные пробелы!
    date: Optional[date] = None

# ----------------------------------------------------
# 7. BALANCE (Баланс) СХЕМА
# ----------------------------------------------------
class BalanceResponse(BaseModel):
    total_income: float
    total_expenses: float
    net_balance: float

# --- Statistics Schema ---
class CategoryStats(BaseModel):
    category_name: str
    total_amount: float