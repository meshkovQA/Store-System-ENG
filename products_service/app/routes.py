from fastapi import APIRouter, Depends, HTTPException, status, Query
import asyncio
from sqlalchemy.orm import Session
from uuid import UUID
from app import crud, schemas, database, auth, logger
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.database import get_session_local


router = APIRouter()

security = HTTPBearer()


@router.post("/products/", response_model=schemas.Product, status_code=status.HTTP_201_CREATED, tags=["Products Service"], summary="Create a new product")
async def create_product(product: schemas.ProductCreate, db: Session = Depends(get_session_local), credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    user_data = auth.verify_token_in_other_service(
        token)
    logger.log_message(
        f"User {user_data}")
    if not user_data:
        logger.log_message("Invalid token or unauthorized access")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid token or unauthorized access")

    logger.log_message(f"User {user_data} is creating a new product")
    return crud.create_product(db=db, name=product.name, description=product.description, user_id=user_data,
                               category=product.category, price=product.price, stock_quantity=product.stock_quantity,
                               supplier_id=product.supplier_id, image_url=product.image_url, weight=product.weight,
                               dimensions=product.dimensions, manufacturer=product.manufacturer)


@router.get("/products/", response_model=list[schemas.ProductResponse], tags=["Products Service"], summary="Get all products")
def get_products(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_session_local)):
    token = credentials.credentials
    user_data = auth.verify_token_in_other_service(
        token)
    if not user_data:
        logger.log_message("Invalid token or unauthorized access")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid token or unauthorized access")
    logger.log_message("Getting all products")
    return crud.get_all_products(db)


@router.get("/products/{product_id}", response_model=schemas.Product, tags=["Products Service"], summary="Get product by ID")
def get_product(product_id: str, db: Session = Depends(get_session_local), credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    user_data = auth.verify_token_in_other_service(
        token)  #
    if not user_data:
        logger.log_message("Invalid token or unauthorized access")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid token or unauthorized access")
    logger.log_message(f"Getting product with id {product_id}")
    return crud.get_product_by_id(db, product_id)


@router.put("/products/{product_id}", response_model=schemas.Product, tags=["Products Service"], summary="Update product by ID")
async def update_product(product_id: str, product: schemas.ProductUpdate, db: Session = Depends(get_session_local), credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    user_data = auth.verify_token_in_other_service(token)
    if not user_data:
        logger.log_message("Invalid token or unauthorized access")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid token or unauthorized access")

    user_id = user_data.get("user_id") if "user_id" in user_data else None
    logger.log_message(
        f"""User {user_id} is updating product with id {product_id}, new name: {product.name}, new description: {product.description}, new price: {product.price}""")
    return crud.update_product(db=db, product_id=product_id, name=product.name, description=product.description, user_id=user_id,
                               category=product.category, price=product.price, stock_quantity=product.stock_quantity,
                               supplier_id=product.supplier_id, image_url=product.image_url, weight=product.weight,
                               dimensions=product.dimensions, manufacturer=product.manufacturer)


@router.patch("/products/{product_id}", response_model=schemas.Product, tags=["Products Service"], summary="Partially update availablity of product by ID")
async def partial_update_product(product_id: str, availability_data: schemas.ProductAvailabilityUpdate, db: Session = Depends(get_session_local), credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    user_data = auth.verify_token_in_other_service(token)
    if not user_data:
        logger.log_message("Invalid token or unauthorized access")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid token or unauthorized access")

    user_id = user_data.get("user_id") if "user_id" in user_data else None
    logger.log_message(
        f"User {user_id} is partially updating product with id {product_id}")

    return crud.update_product_availability(db=db, product_id=product_id, is_available=availability_data.is_available)


@router.delete("/products/{product_id}", tags=["Products Service"], summary="Delete product by ID")
def delete_product(product_id: str, db: Session = Depends(get_session_local), credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    user_data = auth.verify_token_in_other_service(
        token)
    if not user_data:
        logger.log_message("Invalid token or unauthorized access")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid token or unauthorized access")
    logger.log_message(f"Deleting product with id {product_id}")
    return crud.delete_product(db, product_id)


@router.get("/search_products/", response_model=list[schemas.Product], tags=["Products Service"], summary="Search products by name")
def search_products(name: str, db: Session = Depends(get_session_local), credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    user_data = auth.verify_token_in_other_service(token)
    if not user_data:
        logger.log_message("Invalid token or unauthorized access")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid token or unauthorized access")

    logger.log_message(f"Searching products with name containing '{name}'")
    return crud.search_products_by_name(db, name)

# ---- CRUD операции для поставщиков (Supplier) ----


@router.post("/suppliers/", response_model=schemas.Supplier, tags=["Suppliers Service"], status_code=status.HTTP_201_CREATED, summary="Create a new supplier")
def create_supplier(supplier: schemas.SupplierCreate, db: Session = Depends(get_session_local), credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    user_data = auth.verify_token_in_other_service(
        token)  # Проверяем токен через auth.py
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


@router.get("/suppliers/", response_model=list[schemas.Supplier], tags=["Suppliers Service"], summary="Get all suppliers")
def get_all_suppliers(db: Session = Depends(get_session_local), credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    user_data = auth.verify_token_in_other_service(
        token)  # Проверяем токен через auth.py
    if not user_data:
        logger.log_message("Invalid token or unauthorized access")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid token or unauthorized access")
    logger.log_message("Getting all suppliers")
    return crud.get_all_suppliers(db)


@router.get("/suppliers/{supplier_id}", response_model=schemas.Supplier, tags=["Suppliers Service"], summary="Get supplier by ID")
def get_supplier_by_id(supplier_id: str, db: Session = Depends(get_session_local), credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    user_data = auth.verify_token_in_other_service(
        token)
    if not user_data:
        logger.log_message("Invalid token or unauthorized access")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid token or unauthorized access")
    logger.log_message(f"Getting supplier with ID {supplier_id}")
    return crud.get_supplier_by_id(db, supplier_id)


@router.patch("/suppliers/{supplier_id}", response_model=schemas.Supplier, tags=["Suppliers Service"], summary="Update supplier by ID")
def patch_supplier(supplier_id: str, supplier: schemas.SupplierUpdate, db: Session = Depends(get_session_local), credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    user_data = auth.verify_token_in_other_service(
        token)
    if not user_data:
        logger.log_message("Invalid token or unauthorized access")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid token or unauthorized access")
    # Передаем только те поля, которые изменены
    updates = supplier.dict(exclude_unset=True)
    logger.log_message(f"Updating supplier with id {supplier_id}")
    return crud.patch_supplier(db=db, supplier_id=supplier_id, updates=updates)


@router.delete("/suppliers/{supplier_id}", tags=["Suppliers Service"], summary="Delete supplier by ID")
def delete_supplier(supplier_id: str, db: Session = Depends(get_session_local), credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    user_data = auth.verify_token_in_other_service(
        token)
    if not user_data:
        logger.log_message("Invalid token or unauthorized access")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid token or unauthorized access")
    logger.log_message(f"Deleting supplier with id {supplier_id}")
    return crud.delete_supplier(db, supplier_id)


@router.get("/search_suppliers/", response_model=list[schemas.Supplier], tags=["Suppliers Service"], summary="Search suppliers by name")
def search_suppliers(name: str, db: Session = Depends(get_session_local), credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    user_data = auth.verify_token_in_other_service(token)
    if not user_data:
        logger.log_message("Invalid token or unauthorized access")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid token or unauthorized access")

    logger.log_message(f"Searching suppliers with name containing '{name}'")
    return crud.search_suppliers_by_name(db, name)


@router.get("/warehouses/{warehouse_id}", response_model=schemas.Warehouse, tags=["Warehouses Service"], summary="Get warehouse by ID")
def get_warehouse_by_id(warehouse_id: UUID, db: Session = Depends(get_session_local), credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    user_data = auth.verify_token_in_other_service(
        token)
    if not user_data:
        logger.log_message("Invalid token or unauthorized access")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid token or unauthorized access")
    logger.log_message(f"Getting warehouse with id {warehouse_id}")
    return crud.get_warehouse_by_id(db, warehouse_id=str(warehouse_id))


@router.get("/warehouses/", response_model=list[schemas.Warehouse], tags=["Warehouses Service"], summary="Get all warehouses")
def get_all_warehouses(db: Session = Depends(get_session_local), credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    user_data = auth.verify_token_in_other_service(token)
    if not user_data:
        logger.log_message("Invalid token or unauthorized access")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid token or unauthorized access")

    logger.log_message("Getting all warehouses")
    return crud.get_all_warehouses(db)


@router.post("/warehouses/", response_model=schemas.Warehouse, tags=["Warehouses Service"], summary="Create a new warehouse")
def create_warehouse(warehouse: schemas.WarehouseCreate, db: Session = Depends(get_session_local), credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    user_data = auth.verify_token_in_other_service(
        token)
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


@router.patch("/warehouses/{warehouse_id}", response_model=schemas.Warehouse, tags=["Warehouses Service"], summary="Update warehouse by ID")
def patch_warehouse(warehouse_id: str, warehouse: schemas.WarehouseUpdate, db: Session = Depends(get_session_local), credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    user_data = auth.verify_token_in_other_service(
        token)
    if not user_data:
        logger.log_message("Invalid token or unauthorized access")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid token or unauthorized access")
    updates = warehouse.dict(exclude_unset=True)
    logger.log_message(f"Updating warehouse with id {warehouse_id}")
    return crud.patch_warehouse(db=db, warehouse_id=warehouse_id, updates=updates)


@router.delete("/warehouses/{warehouse_id}", tags=["Warehouses Service"], summary="Delete warehouse by ID")
def delete_warehouse(warehouse_id: UUID, db: Session = Depends(get_session_local), credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    user_data = auth.verify_token_in_other_service(
        token)
    if not user_data:
        logger.log_message("Invalid token or unauthorized access")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid token or unauthorized access")
    logger.log_message(f"Deleting warehouse with id {warehouse_id}")
    return crud.delete_warehouse(db, warehouse_id=str(warehouse_id))


@router.get("/productinwarehouses/{warehouse_id}", response_model=list[schemas.ProductWarehouse], tags=["Product Warehouses Service"], summary="Get products in warehouse")
def get_products_in_warehouse(warehouse_id: UUID, db: Session = Depends(get_session_local), credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    user_data = auth.verify_token_in_other_service(
        token)
    if not user_data:
        logger.log_message("Invalid token or unauthorized access")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid token or unauthorized access")
    logger.log_message(f"Getting products in warehouse {warehouse_id}")
    return crud.get_products_in_warehouse(db, warehouse_id=str(warehouse_id))


@router.post("/productinwarehouses", response_model=schemas.ProductWarehouse, tags=["Product Warehouses Service"], summary="Add product to warehouse")
def add_product_to_warehouse(
        warehouse_id: UUID = Query(...),
        product_id: UUID = Query(...),
        quantity: int = Query(...),
        db: Session = Depends(get_session_local),
        credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    user_data = auth.verify_token_in_other_service(token)
    if not user_data:
        logger.log_message("Invalid token or unauthorized access")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid token or unauthorized access")

    logger.log_message(f"""Adding product {product_id} to warehouse {
                       warehouse_id} with quantity {quantity}""")
    return crud.add_product_to_warehouse(db=db, product_id=str(product_id), warehouse_id=str(warehouse_id), quantity=quantity)


@router.put("/productinwarehouses/{product_id}", response_model=schemas.ProductWarehouse, tags=["Product Warehouses Service"], summary="Update product in warehouse")
def update_product_in_warehouse(
        product_warehouse_id: UUID,
        quantity: int,
        db: Session = Depends(get_session_local),
        credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    user_data = auth.verify_token_in_other_service(
        token)
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


@router.delete("/productinwarehouses/{product_id}", tags=["Product Warehouses Service"], summary="Delete product from warehouse")
def delete_product_from_warehouse(product_warehouse_id: UUID, db: Session = Depends(get_session_local), credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    user_data = auth.verify_token_in_other_service(
        token)
    if not user_data:
        logger.log_message("Invalid token or unauthorized access")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid token or unauthorized access")
    logger.log_message(f"""Deleting product from warehouse {
                       product_warehouse_id}""")
    return crud.delete_product_from_warehouse(db, product_warehouse_id=str(product_warehouse_id))
