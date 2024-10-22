from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas
from database import SessionLocal, init_db
from passlib.context import CryptContext  # Для работы с хэшированием паролей

app = FastAPI()

# Контекст для хэширования паролей с использованием bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Создание базы данных при старте приложения
init_db()


# Функция для хэширования пароля
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


# Dependency для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Вспомогательная функция для аутентификации пользователя, получения всех заказов или конкретного заказа
def authenticate_user_and_get_orders(user_id: int, password: str, db: Session, order_id: int = None):
    # Находим пользователя по id
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Проверяем пароль
    if not pwd_context.verify(password, db_user.password):
        raise HTTPException(status_code=401, detail="Incorrect password")

    # Если передан `order_id`, возвращаем конкретный заказ, иначе — все заказы
    if order_id:
        db_order = db.query(models.Order).filter(
            (models.Order.user_id == user_id) & (models.Order.id == order_id)
        ).first()
        if not db_order:
            raise HTTPException(status_code=404, detail="Order not found")
        return db_order
    else:
        db_orders = db.query(models.Order).filter(models.Order.user_id == user_id).all()
        if not db_orders:
            raise HTTPException(status_code=404, detail="Orders not found")
        return db_orders


# Добавление пользователя в БД
@app.post("/users/", response_model=schemas.UserOut)
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Проверяем, существует ли пользователь с таким email
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists")

    # Создаем нового пользователя
    db_user = models.User(
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        password=hash_password(user.password)
    )

    # Обработка возможных ошибок при добавлении пользователя в БД
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while creating the user") from e

    return db_user


# Добавление товара в БД
@app.post("/product/", response_model=schemas.ProductOut)
async def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


# Получение данных о товарах из БД по названию товара
@app.get("/products/{name}", response_model=list[schemas.ProductOut])
async def get_products(name: str, db: Session = Depends(get_db)):
    db_product = db.query(models.Product).filter(models.Product.name == name).all()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product


# Создание заказа
@app.post("/order/", response_model=schemas.CreateOrder)
async def order_create(order: schemas.CreateOrder, db: Session = Depends(get_db)):
    db_order = models.Order(**order.dict())
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order


# Получение всех заказов пользователя по id
@app.get("/orders_get/{id}/{password}", response_model=list[schemas.OrdersOut])
async def get_orders_user(id: int, password: str, db: Session = Depends(get_db)):
    db_orders = authenticate_user_and_get_orders(id, password, db)
    return db_orders


# Меняем дату заказа в БД
@app.put("/order_put/{user_id}/{password}/{order_id}/{new_date}/", response_model=schemas.OrderResponse)
async def update_item(user_id: int, password: str, order_id: int, new_date: datetime, db: Session = Depends(get_db)):
    db_order = authenticate_user_and_get_orders(user_id, password, db, order_id=order_id)

    # Обновляем дату заказа
    db_order.order_date = new_date
    db.commit()
    db.refresh(db_order)

    return schemas.OrderResponse(
        id=db_order.id,
        user_id=db_order.user_id,
        order_date=db_order.order_date,
        product_id=db_order.product_id,
        status=db_order.status
    )


# Удаляем заказ из БД
@app.delete("/order/{user_id}/{password}/{order_id}/", response_model=schemas.OrderResponse)
async def delete_order(user_id: int, password: str, order_id: int, db: Session = Depends(get_db)):
    db_order = authenticate_user_and_get_orders(user_id, password, db, order_id=order_id)

    # Удаляем заказ
    db.delete(db_order)
    db.commit()

    return schemas.OrderResponse(
        id=db_order.id,
        user_id=db_order.user_id,
        order_date=db_order.order_date,
        product_id=db_order.product_id,
        status=db_order.status
    )
