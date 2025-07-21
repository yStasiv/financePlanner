from sqlalchemy.orm import Session, joinedload
from typing import Optional
from datetime import date
from . import models, schemas
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_expenses(db: Session, owner_id: int, start_date: Optional[date] = None, end_date: Optional[date] = None, category_id: Optional[int] = None, skip: int = 0, limit: int = 100):
    query = db.query(models.Expense).options(joinedload(models.Expense.category)).filter(models.Expense.owner_id == owner_id)
    if start_date:
        query = query.filter(models.Expense.date >= start_date)
    if end_date:
        query = query.filter(models.Expense.date <= end_date)
    if category_id:
        query = query.filter(models.Expense.category_id == category_id)
    return query.offset(skip).limit(limit).all()


def create_user_expense(db: Session, expense: schemas.ExpenseCreate, user_id: int):
    db_expense = models.Expense(**expense.dict(), owner_id=user_id)
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense


def get_incomes(db: Session, owner_id: int, start_date: Optional[date] = None, end_date: Optional[date] = None, category_id: Optional[int] = None, skip: int = 0, limit: int = 100):
    query = db.query(models.Income).options(joinedload(models.Income.category)).filter(models.Income.owner_id == owner_id)
    if start_date:
        query = query.filter(models.Income.date >= start_date)
    if end_date:
        query = query.filter(models.Income.date <= end_date)
    if category_id:
        query = query.filter(models.Income.category_id == category_id)
    return query.offset(skip).limit(limit).all()


def create_user_income(db: Session, income: schemas.IncomeCreate, user_id: int):
    db_income = models.Income(**income.dict(), owner_id=user_id)
    db.add(db_income)
    db.commit()
    db.refresh(db_income)
    return db_income


def get_expense_categories(db: Session, owner_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.ExpenseCategory).filter(models.ExpenseCategory.owner_id == owner_id).offset(skip).limit(limit).all()


def create_expense_category(db: Session, category: schemas.ExpenseCategoryCreate, owner_id: int):
    db_category = models.ExpenseCategory(**category.dict(), owner_id=owner_id)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def get_income_categories(db: Session, owner_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.IncomeCategory).filter(models.IncomeCategory.owner_id == owner_id).offset(skip).limit(limit).all()


def create_income_category(db: Session, category: schemas.IncomeCategoryCreate, owner_id: int):
    db_category = models.IncomeCategory(**category.dict(), owner_id=owner_id)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def delete_expense(db: Session, expense_id: int, owner_id: int):
    db.query(models.Expense).filter(models.Expense.id == expense_id, models.Expense.owner_id == owner_id).delete()
    db.commit()


def delete_income(db: Session, income_id: int, owner_id: int):
    db.query(models.Income).filter(models.Income.id == income_id, models.Income.owner_id == owner_id).delete()
    db.commit()


def delete_expense_category(db: Session, category_id: int, owner_id: int):
    db.query(models.ExpenseCategory).filter(models.ExpenseCategory.id == category_id, models.ExpenseCategory.owner_id == owner_id).delete()
    db.commit()


def delete_income_category(db: Session, category_id: int, owner_id: int):
    db.query(models.IncomeCategory).filter(models.IncomeCategory.id == category_id, models.IncomeCategory.owner_id == owner_id).delete()
    db.commit()