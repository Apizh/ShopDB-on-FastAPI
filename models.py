from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


# Модель таблицы "Пользователи"
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(length=50), nullable=False)
    last_name = Column(String(length=100), nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String(length=50), nullable=False)

    orders = relationship("Order", back_populates="user")


# Модель таблицы "Товары"
class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(length=100), nullable=False)
    description = Column(String(length=300))
    price = Column(Float, nullable=False)

    orders = relationship("Order", back_populates="product")


# Модель таблицы "Заказы"
class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    order_date = Column(DateTime, nullable=False)
    status = Column(String, nullable=False)

    user = relationship("User", back_populates="orders")
    product = relationship("Product", back_populates="orders")