from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


# ---- Схемы для товаров (Product) ----

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    price: float
    stock_quantity: int
    supplier_id: UUID
    image_url: Optional[str] = None
    weight: Optional[float] = None
    dimensions: Optional[str] = None
    manufacturer: Optional[str] = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(ProductBase):
    pass


class Product(ProductBase):
    product_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# ---- Схемы для поставщиков (Supplier) ----

class SupplierBase(BaseModel):
    name: str
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    website: Optional[str] = None


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    website: Optional[str] = None

    class Config:
        orm_mode = True


class Supplier(SupplierBase):
    supplier_id: UUID

    class Config:
        orm_mode = True


# ---- Схемы для складов (Warehouse) ----

class WarehouseBase(BaseModel):
    location: str
    manager_name: Optional[str] = None
    capacity: int
    current_stock: int
    contact_number: Optional[str] = None
    email: Optional[str] = None
    is_active: bool
    area_size: Optional[float] = None


class WarehouseCreate(WarehouseBase):
    pass


class WarehouseUpdate(WarehouseBase):
    pass


class Warehouse(WarehouseBase):
    warehouse_id: UUID

    class Config:
        orm_mode = True


# ---- Схемы для товаров на складах (ProductWarehouse) ----

class ProductWarehouseBase(BaseModel):
    product_id: UUID
    warehouse_id: UUID
    quantity: int


class ProductWarehouseCreate(ProductWarehouseBase):
    pass


class ProductWarehouseUpdate(BaseModel):
    quantity: int


class ProductWarehouse(ProductWarehouseBase):
    product_warehouse_id: UUID

    class Config:
        orm_mode = True
