from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import models
from ..database import get_db
from ..auth import get_current_active_user

router = APIRouter()

@router.get("/investments")
def get_investments(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    # Знаходимо всі категорії інвестицій
    categories = db.query(models.ExpenseCategory).filter(
        models.ExpenseCategory.owner_id == current_user.id,
        (models.ExpenseCategory.name.ilike('%інвестиці%') | models.ExpenseCategory.name.ilike('%invest%'))
    ).all()
    investments = []
    total_invested = 0
    for category in categories:
        expenses = db.query(models.Expense).filter(models.Expense.owner_id == current_user.id, models.Expense.category_id == category.id).all()
        category_sum = sum([e.amount for e in expenses])
        total_invested += category_sum
        investments.append({
            "category": category.name,
            "sum": category_sum,
            "expenses": [{"amount": e.amount, "description": e.description, "date": e.date} for e in expenses]
        })
    return {"total_invested": total_invested, "investments": investments}
