from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from kafka import KafkaConsumer
from app import crud, schemas, database, auth, logger
import json
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.database import get_session_local


router = APIRouter()

# Создаем объект security для использования схемы авторизации Bearer
security = HTTPBearer()


# Настройка Kafka консьюмера
consumer = KafkaConsumer(
    'products_topic',  # Топик для чтения сообщений
    bootstrap_servers=['localhost:9092'],
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)


def get_token_from_kafka():  # Получение токена из Kafka сообщения
    for message in consumer:
        logger.log_message(f"Received message: {message.value}")
        token = message.value.get('token')
        action = message.value.get('action')
        if token:
            logger.log_message(f"Token found in message: {
                               token} for action: {action}")
            return token
        else:
            logger.log_message("No token found in message")
            raise HTTPException(
                status_code=401, detail="No token found in message")


# ---- Маршруты для CRUD операций с товарами ----

@router.post("/products/", response_model=schemas.Product)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_session_local), credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = get_token_from_kafka()
    user_data = auth.validate_token(token)  # Проверяем токен через auth.py
    if not user_data:
        logger.log_message("Invalid token or unauthorized access")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid token or unauthorized access")
    user_id = user_data['user_id']  # Получаем user_id из токена
    logger.log_message(f"User {user_id} is creating a new product")
    return crud.create_product(db=db, name=product.name, description=product.description, user_id=user_id,
                               category=product.category, price=product.price, stock_quantity=product.stock_quantity,
                               supplier_id=product.supplier_id, image_url=product.image_url, weight=product.weight,
                               dimensions=product.dimensions, manufacturer=product.manufacturer)


@router.get("/products/", response_model=list[schemas.Product])
def get_products(db: Session = Depends(get_session_local), credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = get_token_from_kafka()
    user_data = auth.validate_token(token)  # Проверяем токен через auth.py
    if not user_data:
        logger.log_message("Invalid token or unauthorized access")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid token or unauthorized access")
    logger.log_message("Getting all products")
    return crud.get_all_products(db)


@router.get("/products/{product_id}", response_model=schemas.Product)
def get_product(product_id: str, db: Session = Depends(get_session_local), credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = get_token_from_kafka()
    user_data = auth.validate_token(token)  # Проверяем токен через auth.py
    if not user_data:
        logger.log_message("Invalid token or unauthorized access")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid token or unauthorized access")
    logger.log_message(f"Getting product with id {product_id}")
    return crud.get_product_by_id(db, product_id)


@router.put("/products/{product_id}", response_model=schemas.Product)
def update_product(product_id: str, product: schemas.ProductUpdate, db: Session = Depends(get_session_local), credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = get_token_from_kafka()
    user_data = auth.validate_token(token)  # Проверяем токен через auth.py
    if not user_data:
        logger.log_message("Invalid token or unauthorized access")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid token or unauthorized access")
    user_id = user_data['user_id']     # Получаем user_id из токена
    logger.log_message(
        f"""User {user_id} is updating product with id {product_id}, new name: {product.name}, new description: {product.description}, new price: {product.price}""")
    return crud.update_product(db=db, product_id=product_id, name=product.name, description=product.description, user_id=user_id,
                               category=product.category, price=product.price, stock_quantity=product.stock_quantity,
                               supplier_id=product.supplier_id, image_url=product.image_url, weight=product.weight,
                               dimensions=product.dimensions, manufacturer=product.manufacturer)


@router.delete("/products/{product_id}")
def delete_product(product_id: str, db: Session = Depends(get_session_local), credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = get_token_from_kafka()
    user_data = auth.validate_token(token)  # Проверяем токен через auth.py
    if not user_data:
        logger.log_message("Invalid token or unauthorized access")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid token or unauthorized access")
    logger.log_message(f"Deleting product with id {product_id}")
    return crud.delete_product(db, product_id)


@router.post("/suppliers/", response_model=schemas.Supplier)
def create_supplier(supplier: schemas.SupplierCreate, db: Session = Depends(get_session_local), credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = get_token_from_kafka()
    user_data = auth.validate_token(token)  # Проверяем токен через auth.py
    if not user_data:
        logger.log_message("Invalid token or unauthorized access")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid token or unauthorized access")
    logger.log_message(f"""Creating a new supplier: {supplier.name} {
                       supplier.contact_name}, {supplier.contact_email}, {supplier.phone_number}""")
    return crud.create_supplier(db=db, name=supplier.name, contact_name=supplier.contact_name,
                                contact_email=supplier.contact_email, phone_number=supplier.phone_number,
                                address=supplier.address, country=supplier.country, city=supplier.city,
                                website=supplier.website)


@router.get("/suppliers/", response_model=list[schemas.Supplier])
def get_suppliers(db: Session = Depends(get_session_local), credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = get_token_from_kafka()
    user_data = auth.validate_token(token)  # Проверяем токен через auth.py
    if not user_data:
        logger.log_message("Invalid token or unauthorized access")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid token or unauthorized access")
    logger.log_message("Getting all suppliers")
    return crud.get_all_suppliers(db)


@router.patch("/suppliers/{supplier_id}", response_model=schemas.Supplier)
def patch_supplier(supplier_id: str, supplier: schemas.SupplierUpdate, db: Session = Depends(get_session_local), credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = get_token_from_kafka()
    user_data = auth.validate_token(token)  # Проверяем токен через auth.py
    if not user_data:
        logger.log_message("Invalid token or unauthorized access")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid token or unauthorized access")
    # Передаем только те поля, которые изменены
    updates = supplier.dict(exclude_unset=True)
    logger.log_message(f"Updating supplier with id {supplier_id}")
    return crud.patch_supplier(db=db, supplier_id=supplier_id, updates=updates)


@router.delete("/suppliers/{supplier_id}")
def delete_supplier(supplier_id: str, db: Session = Depends(get_session_local), credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = get_token_from_kafka()
    user_data = auth.validate_token(token)  # Проверяем токен через auth.py
    if not user_data:
        logger.log_message("Invalid token or unauthorized access")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid token or unauthorized access")
    logger.log_message(f"Deleting supplier with id {supplier_id}")
    return crud.delete_supplier(db, supplier_id)

# ---- CRUD операции для складов (Warehouses) ----


@router.post("/warehouses/", response_model=schemas.Warehouse)
def create_warehouse(warehouse: schemas.WarehouseCreate, db: Session = Depends(get_session_local), credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = get_token_from_kafka()
    user_data = auth.validate_token(token)  # Проверяем токен через auth.py
    if not user_data:
        logger.log_message("Invalid token or unauthorized access")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid token or unauthorized access")
    logger.log_message(f"""Creating a new warehouse: {warehouse.location}, {warehouse.manager_name}, {warehouse.capacity}, {
                       warehouse.current_stock}, {warehouse.contact_number}, {warehouse.email}, {warehouse.is_active}, {warehouse.area_size}""")
    return crud.create_warehouse(
        db=db,
        location=warehouse.location,
        manager_name=warehouse.manager_name,
        capacity=warehouse.capacity,
        current_stock=warehouse.current_stock,
        contact_number=warehouse.contact_number,
        email=warehouse.email,
        is_active=warehouse.is_active,
        area_size=warehouse.area_size
    )


@router.get("/warehouses/{warehouse_id}", response_model=schemas.Warehouse)
def get_warehouse_by_id(warehouse_id: UUID, db: Session = Depends(get_session_local), credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = get_token_from_kafka()
    user_data = auth.validate_token(token)  # Проверяем токен через auth.py
    if not user_data:
        logger.log_message("Invalid token or unauthorized access")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid token or unauthorized access")
    logger.log_message(f"Getting warehouse with id {warehouse_id}")
    return crud.get_warehouse_by_id(db, warehouse_id=str(warehouse_id))


@router.delete("/warehouses/{warehouse_id}")
def delete_warehouse(warehouse_id: UUID, db: Session = Depends(get_session_local), credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = get_token_from_kafka()
    user_data = auth.validate_token(token)  # Проверяем токен через auth.py
    if not user_data:
        logger.log_message("Invalid token or unauthorized access")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid token or unauthorized access")
    logger.log_message(f"Deleting warehouse with id {warehouse_id}")
    return crud.delete_warehouse(db, warehouse_id=str(warehouse_id))


# ---- CRUD операции для товаров на складах (ProductWarehouses) ----

@router.post("/warehouses/{warehouse_id}/products/{product_id}", response_model=schemas.ProductWarehouse)
def add_product_to_warehouse(
        warehouse_id: UUID,
        product_id: UUID,
        quantity: int,
        db: Session = Depends(get_session_local), credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = get_token_from_kafka()
    user_data = auth.validate_token(token)  # Проверяем токен через auth.py
    if not user_data:
        logger.log_message("Invalid token or unauthorized access")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid token or unauthorized access")
    logger.log_message(f"""Adding product {
                       product_id} to warehouse {warehouse_id} with quantity {quantity}""")
    return crud.add_product_to_warehouse(
        db=db,
        product_id=str(product_id),
        warehouse_id=str(warehouse_id),
        quantity=quantity
    )


@router.get("/warehouses/{warehouse_id}/products/", response_model=list[schemas.ProductWarehouse])
def get_products_in_warehouse(warehouse_id: UUID, db: Session = Depends(get_session_local), credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = get_token_from_kafka()
    user_data = auth.validate_token(token)  # Проверяем токен через auth.py
    if not user_data:
        logger.log_message("Invalid token or unauthorized access")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid token or unauthorized access")
    logger.log_message(f"Getting products in warehouse {warehouse_id}")
    return crud.get_products_in_warehouse(db, warehouse_id=str(warehouse_id))


@router.put("/warehouses/products/{product_warehouse_id}", response_model=schemas.ProductWarehouse)
def update_product_in_warehouse(
        product_warehouse_id: UUID,
        quantity: int,
        db: Session = Depends(get_session_local),
        credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = get_token_from_kafka()
    user_data = auth.validate_token(token)  # Проверяем токен через auth.py
    if not user_data:
        logger.log_message("Invalid token or unauthorized access")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid token or unauthorized access")
    logger.log_message(f"Updating product in warehouse {product_warehouse_id}")
    return crud.update_product_in_warehouse(
        db=db,
        product_warehouse_id=str(product_warehouse_id),
        quantity=quantity
    )


@router.delete("/warehouses/products/{product_warehouse_id}")
def delete_product_from_warehouse(product_warehouse_id: UUID, db: Session = Depends(get_session_local), credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = get_token_from_kafka()
    user_data = auth.validate_token(token)  # Проверяем токен через auth.py
    if not user_data:
        logger.log_message("Invalid token or unauthorized access")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid token or unauthorized access")
    logger.log_message(f"""Deleting product from warehouse {
                       product_warehouse_id}""")
    return crud.delete_product_from_warehouse(db, product_warehouse_id=str(product_warehouse_id))

    # ---- CRUD операции для товаров на складах (ProductWarehouses) ----


@ router.post("/warehouses/{warehouse_id}/products/{product_id}", response_model=schemas.ProductWarehouse)
def add_product_to_warehouse(
        warehouse_id: UUID,
        product_id: UUID,
        quantity: int,
        db: Session = Depends(get_session_local),
        redentials: HTTPAuthorizationCredentials = Depends(security)):
    token = get_token_from_kafka()
    user_data = auth.validate_token(token)  # Проверяем токен через auth.py
    if not user_data:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid token or unauthorized access")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid token or unauthorized access")
    logger.log_message(f"""Adding product {product_id} to warehouse {
                       warehouse_id} with quantity {quantity}""")
    return crud.add_product_to_warehouse(
        db=db,
        product_id=str(product_id),
        warehouse_id=str(warehouse_id),
        quantity=quantity
    )


@ router.get("/warehouses/{warehouse_id}/products/", response_model=list[schemas.ProductWarehouse])
def get_products_in_warehouse(warehouse_id: UUID, db: Session = Depends(get_session_local), credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = get_token_from_kafka()
    user_data = auth.validate_token(token)  # Проверяем токен через auth.py
    if not user_data:
        logger.log_message("Invalid token or unauthorized access")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid token or unauthorized access")
    logger.log_message(f"Getting products in warehouse {warehouse_id}")
    return crud.get_products_in_warehouse(db, warehouse_id=str(warehouse_id))


@ router.put("/warehouses/products/{product_warehouse_id}", response_model=schemas.ProductWarehouse)
def update_product_in_warehouse(
        product_warehouse_id: UUID,
        quantity: int,
        db: Session = Depends(get_session_local),
        credentials: HTTPAuthorizationCredentials = Depends(security)

):
    token = get_token_from_kafka()
    user_data = auth.validate_token(token)  # Проверяем токен через auth.py
    if not user_data:
        logger.log_message("Invalid token or unauthorized access")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid token or unauthorized access")
    logger.log_message(f"""Updating product in warehouse {
                       product_warehouse_id} with quantity {quantity}""")
    return crud.update_product_in_warehouse(
        db=db,
        product_warehouse_id=str(product_warehouse_id),
        quantity=quantity
    )


@ router.delete("/warehouses/products/{product_warehouse_id}")
def delete_product_from_warehouse(product_warehouse_id: UUID, db: Session = Depends(get_session_local), credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = get_token_from_kafka()
    user_data = auth.validate_token(token)  # Проверяем токен через auth.py
    if not user_data:
        logger.log_message("Invalid token or unauthorized access")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid token or unauthorized access")
    logger.log_message(f"""Deleting product from warehouse {
                       product_warehouse_id}""")
    return crud.delete_product_from_warehouse(db, product_warehouse_id=str(product_warehouse_id))
