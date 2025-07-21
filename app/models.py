from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, Date, UniqueConstraint
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    expenses = relationship("Expense", back_populates="owner")
    incomes = relationship("Income", back_populates="owner")
    expense_categories = relationship("ExpenseCategory", back_populates="owner")
    income_categories = relationship("IncomeCategory", back_populates="owner")


class ExpenseCategory(Base):
    __tablename__ = "expense_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="expense_categories")
    __table_args__ = (UniqueConstraint('name', 'owner_id', name='_owner_expense_category_uc'),)


class IncomeCategory(Base):
    __tablename__ = "income_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="income_categories")
    __table_args__ = (UniqueConstraint('name', 'owner_id', name='_owner_income_category_uc'),)


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, index=True)
    description = Column(String(100), index=True)
    date = Column(Date, index=True)
    category_id = Column(Integer, ForeignKey("expense_categories.id"))
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="expenses")
    category = relationship("ExpenseCategory")


class Income(Base):
    __tablename__ = "incomes"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, index=True)
    description = Column(String, index=True)
    date = Column(Date, index=True)
    category_id = Column(Integer, ForeignKey("income_categories.id"))
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="incomes")
    category = relationship("IncomeCategory")