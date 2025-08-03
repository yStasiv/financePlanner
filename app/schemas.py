from pydantic import BaseModel, Field
from datetime import date
from typing import List, Optional


class ExpenseCategoryBase(BaseModel):
    name: str
    limit: Optional[float] = None


class ExpenseCategoryCreate(ExpenseCategoryBase):
    pass


class ExpenseCategoryUpdate(ExpenseCategoryBase):
    name: Optional[str] = None
    limit: Optional[float] = None


class ExpenseCategory(ExpenseCategoryBase):
    id: int

    class Config:
        orm_mode = True


class IncomeCategoryBase(BaseModel):
    name: str


class IncomeCategoryCreate(IncomeCategoryBase):
    pass


class IncomeCategoryUpdate(IncomeCategoryBase):
    name: Optional[str] = None


class IncomeCategory(IncomeCategoryBase):
    id: int

    class Config:
        orm_mode = True


class ExpenseBase(BaseModel):
    amount: float
    description: Optional[str] = Field(None, max_length=100)
    date: date
    category_id: Optional[int] = None


class ExpenseCreate(ExpenseBase):
    pass


class Expense(ExpenseBase):
    id: int
    owner_id: int
    category: Optional[ExpenseCategory] = None

    class Config:
        orm_mode = True


class ExpenseUpdate(BaseModel):
    amount: Optional[float] = None
    description: Optional[str] = None
    date: Optional[date] = None
    category_id: Optional[int] = None


class IncomeBase(BaseModel):
    amount: float
    description: Optional[str] = None
    date: date
    category_id: Optional[int] = None


class IncomeCreate(IncomeBase):
    pass


class Income(IncomeBase):
    id: int
    owner_id: int
    category: Optional[IncomeCategory] = None

    class Config:
        orm_mode = True


class IncomeUpdate(BaseModel):
    amount: Optional[float] = None
    description: Optional[str] = None
    date: Optional[date] = None
    category_id: Optional[int] = None


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    expenses: List[Expense] = []
    incomes: List[Income] = []

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class FinancialData(BaseModel):
    incomes: List[Income]
    expenses: List[Expense]
    total_incomes: int
    total_expenses: int