from pydantic import BaseModel, Field
from datetime import date
from typing import List, Optional


class ExpenseCategoryBase(BaseModel):
    name: str


class ExpenseCategoryCreate(ExpenseCategoryBase):
    pass


class ExpenseCategory(ExpenseCategoryBase):
    id: int

    class Config:
        orm_mode = True


class IncomeCategoryBase(BaseModel):
    name: str


class IncomeCategoryCreate(IncomeCategoryBase):
    pass


class IncomeCategory(IncomeCategoryBase):
    id: int

    class Config:
        orm_mode = True


class ExpenseBase(BaseModel):
    amount: float
    description: Optional[str] = Field(None, max_length=100)
    date: date
    category_id: int


class ExpenseCreate(ExpenseBase):
    pass


class Expense(ExpenseBase):
    id: int
    owner_id: int
    category: ExpenseCategory

    class Config:
        orm_mode = True


class IncomeBase(BaseModel):
    amount: float
    description: Optional[str] = None
    date: date
    category_id: int


class IncomeCreate(IncomeBase):
    pass


class Income(IncomeBase):
    id: int
    owner_id: int
    category: IncomeCategory

    class Config:
        orm_mode = True


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