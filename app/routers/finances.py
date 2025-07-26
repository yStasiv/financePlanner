from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from .. import crud, models, schemas
from ..database import get_db
from ..auth import get_current_active_user

router = APIRouter()

@router.get("/", response_model=schemas.FinancialData)
def read_finances(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    category_id: Optional[int] = None,
    income_skip: int = 0,
    income_limit: int = 10,
    expense_skip: int = 0,
    expense_limit: int = 10,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    incomes, total_incomes = crud.get_incomes(
        db, owner_id=current_user.id, start_date=start_date, end_date=end_date, category_id=category_id, skip=income_skip, limit=income_limit
    )
    expenses, total_expenses = crud.get_expenses(
        db, owner_id=current_user.id, start_date=start_date, end_date=end_date, category_id=category_id, skip=expense_skip, limit=expense_limit
    )
    return {"incomes": incomes, "expenses": expenses, "total_incomes": total_incomes, "total_expenses": total_expenses}

@router.post("/incomes/", response_model=schemas.Income)
def create_income_for_user(income: schemas.IncomeCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    return crud.create_user_income(db=db, income=income, user_id=current_user.id)

@router.put("/incomes/{income_id}", response_model=schemas.Income)
def update_user_income(income_id: int, income: schemas.IncomeUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    db_income = crud.update_income(db=db, income_id=income_id, income_data=income, owner_id=current_user.id)
    if db_income is None:
        raise HTTPException(status_code=404, detail="Income not found")
    return db_income

@router.delete("/incomes/{income_id}", status_code=204)
def delete_user_income(income_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    crud.delete_income(db=db, income_id=income_id, owner_id=current_user.id)
    return

@router.post("/expenses/", response_model=schemas.Expense)
def create_expense_for_user(expense: schemas.ExpenseCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    return crud.create_user_expense(db=db, expense=expense, user_id=current_user.id)

@router.put("/expenses/{expense_id}", response_model=schemas.Expense)
def update_user_expense(expense_id: int, expense: schemas.ExpenseUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    db_expense = crud.update_expense(db=db, expense_id=expense_id, expense_data=expense, owner_id=current_user.id)
    if db_expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return db_expense

@router.delete("/expenses/{expense_id}", status_code=204)
def delete_user_expense(expense_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    crud.delete_expense(db=db, expense_id=expense_id, owner_id=current_user.id)
    return

@router.get("/income_categories/", response_model=List[schemas.IncomeCategory])
def read_income_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    categories = crud.get_income_categories(db, owner_id=current_user.id, skip=skip, limit=limit)
    return categories

@router.post("/income_categories/", response_model=schemas.IncomeCategory)
def create_income_category_for_user(category: schemas.IncomeCategoryCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    return crud.create_income_category(db=db, category=category, owner_id=current_user.id)

@router.put("/income_categories/{category_id}", response_model=schemas.IncomeCategory)
def update_income_category(category_id: int, category: schemas.IncomeCategoryUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    db_category = crud.update_income_category(db=db, category_id=category_id, category_data=category, owner_id=current_user.id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Income category not found")
    return db_category

@router.delete("/income_categories/{category_id}", status_code=204)
def delete_user_income_category(category_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    # Отримуємо категорію, яку треба видалити
    category_to_delete = db.query(models.IncomeCategory).filter(
        models.IncomeCategory.id == category_id,
        models.IncomeCategory.owner_id == current_user.id
    ).first()

    if not category_to_delete:
        raise HTTPException(status_code=404, detail="Income category not found")

    # Забороняємо видалення категорії "Без категорії"
    if category_to_delete.name == "Uncategorized":
        raise HTTPException(status_code=400, detail="Неможливо видалити стандартну категорію 'Без категорії'")

    # Знаходимо або створюємо категорію "Без категорії"
    default_category = db.query(models.IncomeCategory).filter(
        models.IncomeCategory.name == "Uncategorized",
        models.IncomeCategory.owner_id == current_user.id
    ).first()

    if not default_category:
        # Створюємо нову, якщо не існує
        new_default_category = models.IncomeCategory(name="Uncategorized", owner_id=current_user.id)
        db.add(new_default_category)
        db.flush()  # Отримуємо id для нової категорії
        default_category = new_default_category

    # Перепризначаємо всі доходи з цієї категорії на "Без категорії"
    db.query(models.Income).filter(models.Income.category_id == category_id, models.Income.owner_id == current_user.id).update({"category_id": default_category.id})

    # Видаляємо стару категорію
    db.delete(category_to_delete)
    db.commit()
    return

@router.get("/expense_categories/", response_model=List[schemas.ExpenseCategory])
def read_expense_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    categories = crud.get_expense_categories(db, owner_id=current_user.id, skip=skip, limit=limit)
    return categories

@router.post("/expense_categories/", response_model=schemas.ExpenseCategory)
def create_expense_category_for_user(category: schemas.ExpenseCategoryCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    return crud.create_expense_category(db=db, category=category, owner_id=current_user.id)

@router.put("/expense_categories/{category_id}", response_model=schemas.ExpenseCategory)
def update_expense_category(category_id: int, category: schemas.ExpenseCategoryUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    db_category = crud.update_expense_category(db=db, category_id=category_id, category_data=category, owner_id=current_user.id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Expense category not found")
    return db_category

@router.delete("/expense_categories/{category_id}", status_code=204)
def delete_user_expense_category(category_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    # Отримуємо категорію, яку треба видалити
    category_to_delete = db.query(models.ExpenseCategory).filter(
        models.ExpenseCategory.id == category_id,
        models.ExpenseCategory.owner_id == current_user.id
    ).first()

    if not category_to_delete:
        raise HTTPException(status_code=404, detail="Expense category not found")

    # Забороняємо видалення категорії "Без категорії"
    if category_to_delete.name == "Uncategorized":
        raise HTTPException(status_code=400, detail="Неможливо видалити стандартну категорію 'Без категорії'")

    # Знаходимо або створюємо категорію "Без категорії"
    default_category = db.query(models.ExpenseCategory).filter(
        models.ExpenseCategory.name == "Uncategorized",
        models.ExpenseCategory.owner_id == current_user.id
    ).first()

    if not default_category:
        # Створюємо нову, якщо не існує
        new_default_category = models.ExpenseCategory(name="Uncategorized", owner_id=current_user.id)
        db.add(new_default_category)
        db.flush() # Отримуємо id для нової категорії
        default_category = new_default_category

    # Перепризначаємо всі витрати з цієї категорії на "Без категорії"
    db.query(models.Expense).filter(models.Expense.category_id == category_id, models.Expense.owner_id == current_user.id).update({"category_id": default_category.id})

    # Видаляємо стару категорію
    db.delete(category_to_delete)
    db.commit()
    return