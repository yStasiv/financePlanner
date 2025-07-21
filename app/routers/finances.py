from fastapi import APIRouter, Depends, HTTPException
from datetime import date
from typing import Optional
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas, auth
from ..database import SessionLocal

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/expenses/", response_model=List[schemas.Expense])
def read_expenses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_active_user)):
    expenses = crud.get_expenses(db, skip=skip, limit=limit)
    return expenses

@router.post("/expenses/", response_model=schemas.Expense)
def create_expense(expense: schemas.ExpenseCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_active_user)):
    return crud.create_user_expense(db=db, expense=expense, user_id=current_user.id)

@router.get("/incomes/", response_model=List[schemas.Income])
def read_incomes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_active_user)):
    incomes = crud.get_incomes(db, skip=skip, limit=limit)
    return incomes

@router.post("/incomes/", response_model=schemas.Income)
def create_income(income: schemas.IncomeCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_active_user)):
    return crud.create_user_income(db=db, income=income, user_id=current_user.id)

@router.get("/expense_categories/", response_model=List[schemas.ExpenseCategory])
def read_expense_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_active_user)):
    categories = crud.get_expense_categories(db, owner_id=current_user.id, skip=skip, limit=limit)
    return categories

@router.post("/expense_categories/", response_model=schemas.ExpenseCategory)
def create_expense_category(category: schemas.ExpenseCategoryCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_active_user)):
    return crud.create_expense_category(db=db, category=category, owner_id=current_user.id)

@router.get("/income_categories/", response_model=List[schemas.IncomeCategory])
def read_income_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_active_user)):
    categories = crud.get_income_categories(db, owner_id=current_user.id, skip=skip, limit=limit)
    return categories

@router.post("/income_categories/", response_model=schemas.IncomeCategory)
def create_income_category(category: schemas.IncomeCategoryCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_active_user)):
    return crud.create_income_category(db=db, category=category, owner_id=current_user.id)

@router.get("/finances/", response_model=schemas.FinancialData)
def read_finances(start_date: Optional[date] = None, end_date: Optional[date] = None, category_id: Optional[int] = None, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_active_user)):
    incomes = crud.get_incomes(db, owner_id=current_user.id, start_date=start_date, end_date=end_date, category_id=category_id)
    expenses = crud.get_expenses(db, owner_id=current_user.id, start_date=start_date, end_date=end_date, category_id=category_id)
    return {"incomes": incomes, "expenses": expenses}


@router.delete("/expenses/{expense_id}")
def delete_expense(expense_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_active_user)):
    crud.delete_expense(db=db, expense_id=expense_id, owner_id=current_user.id)
    return {"ok": True}


@router.delete("/incomes/{income_id}")
def delete_income(income_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_active_user)):
    crud.delete_income(db=db, income_id=income_id, owner_id=current_user.id)
    return {"ok": True}


@router.delete("/expense_categories/{category_id}")
def delete_expense_category(category_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_active_user)):
    crud.delete_expense_category(db=db, category_id=category_id, owner_id=current_user.id)
    return {"ok": True}


@router.delete("/income_categories/{category_id}")
def delete_income_category(category_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_active_user)):
    crud.delete_income_category(db=db, category_id=category_id, owner_id=current_user.id)
    return {"ok": True}