from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date, datetime

# 1. USER
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

# 2. CATEGORY
class CategoryCreate(BaseModel):
    name: str
class CategoryResponse(CategoryCreate):
    id: int
    user_id: int
    class Config:
        from_attributes = True

# 3. EXPENSE
class ExpenseCreate(BaseModel):
    amount: float
    description: Optional[str] = None
    category_id: int
    date: date  # Маңызды: date
class ExpenseResponse(ExpenseCreate):
    id: int
    user_id: int
    class Config:
        from_attributes = True

# 4. INCOME
class IncomeCreate(BaseModel):
    amount: float
    description: Optional[str] = None
    category_id: Optional[int] = None
    date: date # Маңызды: date
class IncomeResponse(IncomeCreate):
    id: int
    user_id: int
    class Config:
        from_attributes = True

# 5. BUDGET
class BudgetCreate(BaseModel):
    limit_amount: float
    category_id: int
    start_date: date
    end_date: date
class BudgetResponse(BudgetCreate):
    id: int
    user_id: int
    class Config:
        from_attributes = True

# 6. BALANCE & STATS
class BalanceResponse(BaseModel):
    total_income: float
    total_expenses: float
    net_balance: float
class CategoryStats(BaseModel):
    category_name: str
    total_amount: float