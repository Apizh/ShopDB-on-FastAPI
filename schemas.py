from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


# Модель Pydantic для пользователей
class UserBase(BaseModel):
    first_name: str = Field(..., min_length=2, max_length=50)
    last_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=5, max_length=100)


class UserOut(UserBase):
    id: int = Field(..., gt=0)
    password: str = Field(..., min_length=5, max_length=100)

    class Config:
        from_attributes = True


# Модель Pydantic для товаров
class ProductBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    price: float


class ProductCreate(ProductBase):
    pass


class ProductOut(ProductBase):
    id: int = Field(..., gt=0)  # id: int

    class Config:
        from_attributes = True


# Модель Pydantic для заказов
class OrderBase(BaseModel):
    user_id: int = Field(..., gt=0)
    product_id: int = Field(..., gt=0)
    order_date: datetime
    status: str = Field(..., max_length=100)


# Модель для создания заказа
class CreateOrder(OrderBase):
    pass


class OrdersOut(OrderBase):
    id: int = Field(..., gt=0)

    class Config:
        from_attributes = True


class OrderResponse(OrderBase):
    id: int = Field(..., gt=0)

    class Config:
        from_attributes = True
