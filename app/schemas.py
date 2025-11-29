from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date, datetime

# User
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

# Category
class CategoryCreate(BaseModel):
    name: str
class CategoryResponse(CategoryCreate):
    id: int
    user_id: int
    class Config:
        from_attributes = True

# Expense
class ExpenseCreate(BaseModel):
    amount: float
    description: Optional[str] = None
    category_id: int 
    date: date 
class ExpenseResponse(ExpenseCreate):
    id: int
    user_id: int
    class Config:
        from_attributes = True

# Income
class IncomeCreate(BaseModel):
    amount: float
    description: Optional[str] = None
    date: date 
class IncomeResponse(IncomeCreate):
    id: int
    user_id: int
    class Config:
        from_attributes = True

# Stats
class BalanceResponse(BaseModel):
    total_income: float
    total_expenses: float
    net_balance: float

class CategoryStats(BaseModel):
    category_name: str
    total_amount: float