from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from . import models, schemas
from .utils import get_password_hash

# 1. USER
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email, 
        username=user.username, 
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# 2. CATEGORY
def create_user_category(db: Session, category: schemas.CategoryCreate, user_id: int):
    db_category = models.Category(name=category.name, user_id=user_id)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def get_user_categories(db: Session, user_id: int):
    return db.query(models.Category).filter(models.Category.user_id == user_id).all()

# 3. EXPENSE (ТҮЗЕТІЛГЕН БӨЛІК)
def create_user_expense(db: Session, expense: schemas.ExpenseCreate, user_id: int):
    db_expense = models.Expense(
        amount=expense.amount,
        description=expense.description,
        category_id=expense.category_id,
        user_id=user_id,
        # Мұнда "expense.date" қолданылуы керек
        date=expense.date 
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

def update_user_expense(db: Session, expense_id: int, expense_update: schemas.ExpenseUpdate, user_id: int):
    db_expense = db.query(models.Expense).filter(models.Expense.id == expense_id, models.Expense.user_id == user_id).first()
    if not db_expense:
        return None
    
    update_data = expense_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_expense, key, value)
    
    db.commit()
    db.refresh(db_expense)
    return db_expense

# 4. INCOME (ТҮЗЕТІЛГЕН БӨЛІК)
def create_user_income(db: Session, income: schemas.IncomeCreate, user_id: int):
    db_income = models.Income(
        amount=income.amount,
        description=income.description,
        category_id=income.category_id,
        user_id=user_id,
        # Мұнда "income.date" қолданылуы керек
        date=income.date 
    )
    db.add(db_income)
    db.commit()
    db.refresh(db_income)
    return db_income

def get_user_incomes(db: Session, user_id: int):
    return db.query(models.Income).filter(models.Income.user_id == user_id).all()

# 5. BALANCE
def get_user_balance(db: Session, user_id: int):
    total_income = db.query(func.sum(models.Income.amount)).filter(
        models.Income.user_id == user_id
    ).scalar() or 0
    total_expenses = db.query(func.sum(models.Expense.amount)).filter(
        models.Expense.user_id == user_id
    ).scalar() or 0
    return {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "net_balance": total_income - total_expenses
    }

# 6. STATISTICS
def get_expenses_by_category(db: Session, user_id: int):
    results = db.query(
        models.Category.name, 
        func.sum(models.Expense.amount)
    ).join(models.Expense).filter(
        models.Expense.user_id == user_id
    ).group_by(models.Category.name).all()
    return [{"category_name": name, "total_amount": amount} for name, amount in results]