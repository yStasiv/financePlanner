from fastapi import HTTPException
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
    # базові категорії
    base_income = ["Uncategorized","Зарплата", "Подарунки"]
    base_expense = ["Uncategorized", "Продукти", "Оренда", "Розваги"]
    for name in base_income:
        db.add(models.IncomeCategory(name=name, owner_id=db_user.id))
    for name in base_expense:
        db.add(models.ExpenseCategory(name=name, owner_id=db_user.id))
    db.commit()
    return db_user


def get_expenses(db: Session, owner_id: int, start_date: Optional[date] = None, end_date: Optional[date] = None, category_id: Optional[int] = None, skip: int = 0, limit: int = 100):
    query = db.query(models.Expense).filter(models.Expense.owner_id == owner_id)
    if start_date:
        query = query.filter(models.Expense.date >= start_date)
    if end_date:
        query = query.filter(models.Expense.date <= end_date)
    if category_id:
        query = query.filter(models.Expense.category_id == category_id)
    total = query.count()
    items = query.options(joinedload(models.Expense.category)).offset(skip).limit(limit).all()
    return items, total


def create_user_expense(db: Session, expense: schemas.ExpenseCreate, user_id: int):
    """Create a new expense for the user, checking category limits if applicable."""
    category_id = expense.category_id
    if category_id:
        category = db.query(models.ExpenseCategory).filter(models.ExpenseCategory.id == category_id, models.ExpenseCategory.owner_id == user_id).first()
        
    db_expense = models.Expense(**expense.dict(), owner_id=user_id)
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    if category and category.limit is not None:
            # Сумарні витрати по категорії
            total_expenses = db.query(models.Expense).filter(models.Expense.category_id == category_id, models.Expense.owner_id == user_id).with_entities(models.Expense.amount).all()
            total = sum([e.amount for e in total_expenses]) + expense.amount
            if total > category.limit:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "message": f"Ліміт категорії '{category.name}' перевищено!",
                        "limit": category.limit,
                        "total": total,
                        "exceeded": total - category.limit
                    }
                )
    return db_expense


def get_incomes(db: Session, owner_id: int, start_date: Optional[date] = None, end_date: Optional[date] = None, category_id: Optional[int] = None, skip: int = 0, limit: int = 100):
    query = db.query(models.Income).filter(models.Income.owner_id == owner_id)
    if start_date:
        query = query.filter(models.Income.date >= start_date)
    if end_date:
        query = query.filter(models.Income.date <= end_date)
    if category_id:
        query = query.filter(models.Income.category_id == category_id)
    total = query.count()
    items = query.options(joinedload(models.Income.category)).offset(skip).limit(limit).all()
    return items, total


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


def update_income(db: Session, income_id: int, income_data: schemas.IncomeUpdate, owner_id: int):
    db_income = db.query(models.Income).filter(models.Income.id == income_id, models.Income.owner_id == owner_id).first()
    if db_income:
        update_data = income_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_income, key, value)
        db.commit()
        db.refresh(db_income)
    return db_income


def update_expense(db: Session, expense_id: int, expense_data: schemas.ExpenseUpdate, owner_id: int):
    db_expense = db.query(models.Expense).filter(models.Expense.id == expense_id, models.Expense.owner_id == owner_id).first()
    if db_expense:
        update_data = expense_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_expense, key, value)
        db.commit()
        db.refresh(db_expense)
    return db_expense


def update_income_category(db: Session, category_id: int, category_data: schemas.IncomeCategoryUpdate, owner_id: int):
    db_category = db.query(models.IncomeCategory).filter(models.IncomeCategory.id == category_id, models.IncomeCategory.owner_id == owner_id).first()
    if db_category:
        if db_category.name == "Uncategorized":
            raise HTTPException(status_code=400, detail="Cannot rename the default category 'Uncategorized'")
        update_data = category_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_category, key, value)
        db.commit()
        db.refresh(db_category)
    return db_category


def update_expense_category(db: Session, category_id: int, category_data: schemas.ExpenseCategoryUpdate, owner_id: int):
    """Update/rename an existing expense category."""
    db_category = db.query(models.ExpenseCategory).filter(models.ExpenseCategory.id == category_id, models.ExpenseCategory.owner_id == owner_id).first()
    if db_category:
        if db_category.name == "Uncategorized":
            raise HTTPException(status_code=400, detail="Cannot rename the default category 'Uncategorized'")
        update_data = category_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_category, key, value)
        db.commit()
        db.refresh(db_category)
    return db_category