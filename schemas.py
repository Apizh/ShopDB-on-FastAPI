from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# Модель Pydantic для пользователей
class UserBase(BaseModel):
    first_name: str
    last_name: str
    email: str


class UserCreate(UserBase):
    password: str


class UserOut(UserBase):
    id: int

    class Config:
        orm_mode = True


# Модель Pydantic для товаров
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float


class ProductCreate(ProductBase):
    pass


class ProductOut(ProductBase):
    id: int

    class Config:
        orm_mode = True


# Модель Pydantic для заказов
class OrderBase(BaseModel):
    user_id: int
    product_id: int
    order_date: datetime
    status: str


class OrderCreate(OrderBase):
    pass


class OrderOut(OrderBase):
    id: int

    class Config:
        orm_mode = True
