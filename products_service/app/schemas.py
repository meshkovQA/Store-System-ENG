from pydantic import BaseModel, Field, constr, validator, conint, condecimal
from typing import Optional
from uuid import UUID
from datetime import datetime


# ---- Схемы для товаров (Product) ----

class ProductBase(BaseModel):
    name: constr(min_length=1, max_length=100)
    description: Optional[constr(max_length=500)] = None
    category: Optional[constr(max_length=50)] = None
    price: condecimal(gt=0, max_digits=10, decimal_places=2)
    stock_quantity: conint(ge=0)
    supplier_id: str
    image_url: Optional[constr(max_length=255)] = None
    weight: Optional[condecimal(gt=0, max_digits=6, decimal_places=2)] = None
    dimensions: Optional[constr(max_length=100)] = None
    manufacturer: Optional[constr(max_length=100)] = None


class ProductResponse(BaseModel):
    product_id: str
    user_id: str
    name: str
    description: str
    category: str
    price: float
    stock_quantity: int
    supplier_id: str  # Преобразуем UUID в строку
    is_available: bool
    created_at: datetime
    updated_at: datetime
    image_url: str
    weight: float
    dimensions: str
    manufacturer: str

    class Config:
        orm_mode = True


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


class ProductAvailabilityUpdate(BaseModel):
    is_available: bool


# ---- Схемы для поставщиков (Supplier) ----

class SupplierBase(BaseModel):
    name: constr(min_length=1, max_length=100)
    contact_name: Optional[constr(max_length=100)] = None
    contact_email: Optional[constr(max_length=100)] = None
    phone_number: Optional[constr(max_length=15)] = None
    address: Optional[constr(max_length=200)] = None
    country: Optional[constr(max_length=50)] = None
    city: Optional[constr(max_length=50)] = None
    website: Optional[constr(max_length=255)] = None


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(BaseModel):
    name: Optional[constr(min_length=1, max_length=100)] = None
    contact_name: Optional[constr(max_length=100)] = None
    contact_email: Optional[constr(max_length=100)] = None
    phone_number: Optional[constr(max_length=15)] = None
    address: Optional[constr(max_length=200)] = None
    country: Optional[constr(max_length=50)] = None
    city: Optional[constr(max_length=50)] = None
    website: Optional[constr(max_length=255)] = None

    class Config:
        orm_mode = True


class Supplier(SupplierBase):
    supplier_id: UUID

    class Config:
        orm_mode = True


class SupplierSearch(BaseModel):
    name: Optional[constr(min_length=1, max_length=100)] = None

# ---- Схемы для складов (Warehouse) ----


class WarehouseBase(BaseModel):
    location: constr(min_length=1, max_length=100)
    manager_name: Optional[constr(max_length=100)] = None
    capacity: conint(gt=0)
    current_stock: conint(ge=0)
    contact_number: Optional[constr(max_length=15)] = None
    email: Optional[constr(max_length=100)] = None
    is_active: bool
    area_size: Optional[condecimal(
        gt=0, max_digits=7, decimal_places=2)] = None


class WarehouseCreate(WarehouseBase):
    pass


class WarehouseUpdate(WarehouseBase):
    location: constr(min_length=1, max_length=100)
    manager_name: Optional[constr(max_length=100)] = None
    capacity: conint(gt=0)
    current_stock: conint(ge=0)
    contact_number: Optional[constr(max_length=15)] = None
    email: Optional[constr(max_length=100)] = None
    is_active: bool
    area_size: Optional[condecimal(
        gt=0, max_digits=7, decimal_places=2)] = None

    class Config:
        orm_mode = True


class Warehouse(WarehouseBase):
    warehouse_id: UUID

    class Config:
        orm_mode = True


# ---- Схемы для товаров на складах (ProductWarehouse) ----

class ProductWarehouseBase(BaseModel):
    product_id: UUID
    warehouse_id: UUID
    quantity: conint(ge=0)


class ProductWarehouseCreate(ProductWarehouseBase):
    pass


class ProductWarehouseUpdate(BaseModel):
    quantity: conint(ge=0)


class ProductWarehouse(ProductWarehouseBase):
    product_warehouse_id: UUID

    class Config:
        orm_mode = True
