from sqlalchemy.orm import Session
from uuid import uuid4
from . import models
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError

# ---- CRUD операции для товаров (Products) ----


def create_product(db: Session, name: str, description: str, category: str, price: float, stock_quantity: int, supplier_id: str, image_url: str, weight: float, dimensions: str, manufacturer: str):
    try:
        # Проверка существования поставщика
        supplier = db.query(models.Supplier).filter(
            models.Supplier.supplier_id == supplier_id).first()
        if not supplier:
            raise HTTPException(status_code=404, detail="Supplier not found")

        product_id = str(uuid4())
        new_product = models.Product(
            product_id=product_id,
            name=name,
            description=description,
            category=category,
            price=price,
            stock_quantity=stock_quantity,
            supplier_id=supplier_id,
            image_url=image_url,
            weight=weight,
            dimensions=dimensions,
            manufacturer=manufacturer
        )
        db.add(new_product)
        db.commit()
        db.refresh(new_product)
        return new_product
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Database error: {str(e)}")


def get_all_products(db: Session):
    try:
        return db.query(models.Product).all()
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500, detail=f"Database error: {str(e)}")


def get_product_by_id(db: Session, product_id: str):
    product = db.query(models.Product).filter(
        models.Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


def update_product(db: Session, product_id: str, name: str, description: str, category: str, price: float, stock_quantity: int, supplier_id: str, image_url: str, weight: float, dimensions: str, manufacturer: str):
    try:
        product = db.query(models.Product).filter(
            models.Product.product_id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Проверка существования поставщика
        supplier = db.query(models.Supplier).filter(
            models.Supplier.supplier_id == supplier_id).first()
        if not supplier:
            raise HTTPException(status_code=404, detail="Supplier not found")

        product.name = name
        product.description = description
        product.category = category
        product.price = price
        product.stock_quantity = stock_quantity
        product.supplier_id = supplier_id
        product.image_url = image_url
        product.weight = weight
        product.dimensions = dimensions
        product.manufacturer = manufacturer
        db.commit()
        return product
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Database error: {str(e)}")


def delete_product(db: Session, product_id: str):
    try:
        product = db.query(models.Product).filter(
            models.Product.product_id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        db.delete(product)
        db.commit()
        return {"message": "Product deleted"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Database error: {str(e)}")

# ---- CRUD операции для поставщиков (Suppliers) ----


def create_supplier(db: Session, name: str, contact_name: str, contact_email: str, phone_number: str, address: str, country: str, city: str, website: str):
    try:
        supplier_id = str(uuid4())
        new_supplier = models.Supplier(
            supplier_id=supplier_id,
            name=name,
            contact_name=contact_name,
            contact_email=contact_email,
            phone_number=phone_number,
            address=address,
            country=country,
            city=city,
            website=website
        )
        db.add(new_supplier)
        db.commit()
        db.refresh(new_supplier)
        return new_supplier
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Database error: {str(e)}")


def get_supplier_by_id(db: Session, supplier_id: str):
    supplier = db.query(models.Supplier).filter(
        models.Supplier.supplier_id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier


def patch_supplier(db: Session, supplier_id: str, updates: dict):
    try:
        # Получаем запись поставщика по ID
        supplier = db.query(models.Supplier).filter(
            models.Supplier.supplier_id == supplier_id).first()
        if not supplier:
            raise HTTPException(status_code=404, detail="Supplier not found")

        # Обновляем только те поля, которые переданы в словаре updates
        for key, value in updates.items():
            if hasattr(supplier, key):
                setattr(supplier, key, value)

        db.commit()
        db.refresh(supplier)
        return supplier
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Database error: {str(e)}")


def delete_supplier(db: Session, supplier_id: str):
    try:
        supplier = db.query(models.Supplier).filter(
            models.Supplier.supplier_id == supplier_id).first()
        if not supplier:
            raise HTTPException(status_code=404, detail="Supplier not found")
        db.delete(supplier)
        db.commit()
        return {"message": "Supplier deleted"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Database error: {str(e)}")

# ---- CRUD операции для складов (Warehouses) ----


def create_warehouse(db: Session, location: str, manager_name: str, capacity: int, current_stock: int, contact_number: str, email: str, is_active: bool, area_size: float):
    try:
        warehouse_id = str(uuid4())
        new_warehouse = models.Warehouse(
            warehouse_id=warehouse_id,
            location=location,
            manager_name=manager_name,
            capacity=capacity,
            current_stock=current_stock,
            contact_number=contact_number,
            email=email,
            is_active=is_active,
            area_size=area_size
        )
        db.add(new_warehouse)
        db.commit()
        db.refresh(new_warehouse)
        return new_warehouse
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Database error: {str(e)}")


def get_warehouse_by_id(db: Session, warehouse_id: str):
    warehouse = db.query(models.Warehouse).filter(
        models.Warehouse.warehouse_id == warehouse_id).first()
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return warehouse


def delete_warehouse(db: Session, warehouse_id: str):
    try:
        warehouse = db.query(models.Warehouse).filter(
            models.Warehouse.warehouse_id == warehouse_id).first()
        if not warehouse:
            raise HTTPException(status_code=404, detail="Warehouse not found")
        db.delete(warehouse)
        db.commit()
        return {"message": "Warehouse deleted"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Database error: {str(e)}")

# ---- CRUD операции для товаров на складах (ProductWarehouses) ----


def add_product_to_warehouse(db: Session, product_id: str, warehouse_id: str, quantity: int):
    try:
        # Проверка существования товара
        product = db.query(models.Product).filter(
            models.Product.product_id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Проверка существования склада
        warehouse = db.query(models.Warehouse).filter(
            models.Warehouse.warehouse_id == warehouse_id).first()
        if not warehouse:
            raise HTTPException(status_code=404, detail="Warehouse not found")

        # Создание записи о товаре на складе
        product_warehouse_id = str(uuid4())
        new_record = models.ProductWarehouse(
            product_warehouse_id=product_warehouse_id,
            product_id=product_id,
            warehouse_id=warehouse_id,
            quantity=quantity
        )
        db.add(new_record)
        db.commit()
        return new_record
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Database error: {str(e)}")


def get_products_in_warehouse(db: Session, warehouse_id: str):
    try:
        # Проверка существования склада
        warehouse = db.query(models.Warehouse).filter(
            models.Warehouse.warehouse_id == warehouse_id).first()
        if not warehouse:
            raise HTTPException(status_code=404, detail="Warehouse not found")

        return db.query(models.ProductWarehouse).filter(models.ProductWarehouse.warehouse_id == warehouse_id).all()
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500, detail=f"Database error: {str(e)}")


def update_product_in_warehouse(db: Session, product_warehouse_id: str, quantity: int):
    try:
        # Проверка существования записи
        record = db.query(models.ProductWarehouse).filter(
            models.ProductWarehouse.product_warehouse_id == product_warehouse_id).first()
        if not record:
            raise HTTPException(status_code=404, detail="Record not found")

        record.quantity = quantity
        db.commit()
        return record
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Database error: {str(e)}")


def delete_product_from_warehouse(db: Session, product_warehouse_id: str):
    try:
        # Проверка существования записи
        record = db.query(models.ProductWarehouse).filter(
            models.ProductWarehouse.product_warehouse_id == product_warehouse_id).first()
        if not record:
            raise HTTPException(status_code=404, detail="Record not found")

        db.delete(record)
        db.commit()
        return {"message": "Product removed from warehouse"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Database error: {str(e)}")
