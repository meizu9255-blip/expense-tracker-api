from sqlalchemy.orm import Session
from sqlalchemy import func
from . import models, schemas
from .utils import get_password_hash
from datetime import datetime

# USER
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()
def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(email=user.email, username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# CATEGORY
def create_user_category(db: Session, category: schemas.CategoryCreate, user_id: int):
    db_category = models.Category(name=category.name, user_id=user_id)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category
def get_user_categories(db: Session, user_id: int):
    return db.query(models.Category).filter(models.Category.user_id == user_id).all()

# EXPENSE
def create_user_expense(db: Session, expense: schemas.ExpenseCreate, user_id: int):
    db_expense = models.Expense(
        amount=expense.amount,
        description=expense.description,
        category_id=expense.category_id,
        date=expense.date, # Дұрысталды
        user_id=user_id
    )
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense
def get_user_expenses(db: Session, user_id: int):
    return db.query(models.Expense).filter(models.Expense.user_id == user_id).all()
def delete_user_expense(db: Session, expense_id: int, user_id: int):
    expense = db.query(models.Expense).filter(models.Expense.id == expense_id, models.Expense.user_id == user_id).first()
    if expense:
        db.delete(expense)
        db.commit()
    return expense

# INCOME
def create_user_income(db: Session, income: schemas.IncomeCreate, user_id: int):
    db_income = models.Income(
        amount=income.amount,
        description=income.description,
        category_id=income.category_id,
        date=income.date, # Дұрысталды
        user_id=user_id
    )
    db.add(db_income)
    db.commit()
    db.refresh(db_income)
    return db_income
def get_user_incomes(db: Session, user_id: int):
    return db.query(models.Income).filter(models.Income.user_id == user_id).all()

# BALANCE & STATS
def get_user_balance(db: Session, user_id: int):
    total_income = db.query(func.sum(models.Income.amount)).filter(models.Income.user_id == user_id).scalar() or 0
    total_expenses = db.query(func.sum(models.Expense.amount)).filter(models.Expense.user_id == user_id).scalar() or 0
    return {"total_income": total_income, "total_expenses": total_expenses, "net_balance": total_income - total_expenses}
def get_expenses_by_category(db: Session, user_id: int):
    results = db.query(models.Category.name, func.sum(models.Expense.amount)).join(models.Expense).filter(models.Expense.user_id == user_id).group_by(models.Category.name).all()
    return [{"category_name": name, "total_amount": amount} for name, amount in results]

# BUDGET
def create_budget(db: Session, budget: schemas.BudgetCreate, user_id: int):
    db_budget = models.Budget(
        limit_amount=budget.limit_amount,
        category_id=budget.category_id,
        start_date=budget.start_date,
        end_date=budget.end_date,
        user_id=user_id
    )
    db.add(db_budget)
    db.commit()
    db.refresh(db_budget)
    return db_budget
def get_user_budgets(db: Session, user_id: int):
    return db.query(models.Budget).filter(models.Budget.user_id == user_id).all()