from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

# 1. USER (Қолданушы)
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    
    # БАЙЛАНЫСТАР (Relations)
    categories = relationship("Category", back_populates="owner")
    expenses = relationship("Expense", back_populates="owner")
    incomes = relationship("Income", back_populates="owner")
    
    # МІНЕ, ОСЫ ЖОЛ ЖЕТІСПЕЙ ТҰРҒАН:
    budgets = relationship("Budget", back_populates="owner") 

# 2. CATEGORY (Санаттар)
class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="categories")
    
    expenses = relationship("Expense", back_populates="category")
    incomes = relationship("Income", back_populates="category")
    budgets = relationship("Budget", back_populates="category")

# 3. EXPENSE (Шығындар)
class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float)
    description = Column(String, nullable=True)
    date = Column(DateTime, default=datetime.utcnow)
    
    user_id = Column(Integer, ForeignKey("users.id"))
    category_id = Column(Integer, ForeignKey("categories.id"))
    owner = relationship("User", back_populates="expenses")
    category = relationship("Category", back_populates="expenses")

# 4. INCOME (Кірістер)
class Income(Base):
    __tablename__ = "incomes"
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float)
    description = Column(String, nullable=True)
    date = Column(DateTime, default=datetime.utcnow)
    
    user_id = Column(Integer, ForeignKey("users.id"))
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    owner = relationship("User", back_populates="incomes")
    category = relationship("Category", back_populates="incomes")

# 5. BUDGET (Бюджет)
class Budget(Base):
    __tablename__ = "budgets"
    id = Column(Integer, primary_key=True, index=True)
    limit_amount = Column(Float)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    
    user_id = Column(Integer, ForeignKey("users.id"))
    category_id = Column(Integer, ForeignKey("categories.id"))
    
    # Бұл жерде "back_populates='budgets'" деп тұр, сондықтан User-де де 'budgets' болуы шарт
    owner = relationship("User", back_populates="budgets")
    category = relationship("Category", back_populates="budgets")