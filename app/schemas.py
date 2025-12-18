from pydantic import BaseModel, EmailStr, Field 
from typing import Optional, List
from datetime import date as DateType  

# ----------------------------------------------------
# 1. USER (Қолданушы)
# ----------------------------------------------------
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
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
    amount: float = Field(..., gt=0) 
    description: Optional[str] = None
    category_id: int 
    date: DateType  

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseResponse(ExpenseBase):
    id: int
    date: DateType 
    user_id: int
    class Config:
        from_attributes = True

# ----------------------------------------------------
# 4. INCOME (Кіріс)
# ----------------------------------------------------
class IncomeBase(BaseModel):
    amount: float = Field(..., gt=0)
    description: Optional[str] = None
    category_id: Optional[int] = None
    
class IncomeCreate(IncomeBase):
    date: DateType 

class IncomeResponse(IncomeBase):
    id: int
    date: DateType 
    user_id: int
    class Config:
        from_attributes = True

# ----------------------------------------------------
# 5. BUDGET (Бюджет)
# ----------------------------------------------------
class BudgetBase(BaseModel):
    limit_amount: float = Field(..., gt=0)
    category_id: int
    start_date: DateType 
    end_date: DateType   

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
    amount: Optional[float] = Field(None, gt=0) 
    description: Optional[str] = None
    category_id: Optional[int] = None
    date: Optional[DateType] = None 

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

class TelegramLink(BaseModel):
    telegram_chat_id: str