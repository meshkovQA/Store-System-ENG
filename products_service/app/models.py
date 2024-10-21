import uuid
from sqlalchemy import Column, String, Boolean, Float, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Product(Base):
    __tablename__ = "products"

    product_id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    category = Column(String)           # Категория товара
    price = Column(Float)               # Цена товара
    stock_quantity = Column(Integer)    # Количество на складе
    supplier_name = Column(String)      # Поставщик товара
    is_available = Column(Boolean)      # Доступность для заказа
    created_at = Column(DateTime)       # Дата добавления товара
    updated_at = Column(DateTime)       # Дата последнего обновления информации
    weight = Column(Float)              # Вес товара
    dimensions = Column(String)         # Габариты товара (ДхШхВ)
    manufacturer = Column(String)       # Производитель товара


class Warehouse(Base):
    __tablename__ = "warehouses"

    warehouse_id = Column(String, primary_key=True, index=True)
    location = Column(String)           # Местоположение склада
    manager_name = Column(String)       # Имя управляющего склада
    capacity = Column(Integer)          # Вместимость склада (в ед. товаров)
    current_stock = Column(Integer)     # Текущее количество товаров на складе
    contact_number = Column(String)     # Номер телефона склада
    email = Column(String)              # Контактный email
    is_active = Column(Boolean)         # Активность склада (True/False)
    area_size = Column(Float)           # Площадь склада (в кв.м)
    created_at = Column(DateTime)       # Дата добавления склада


class ProductWarehouse(Base):
    __tablename__ = "product_warehouses"

    product_warehouse_id = Column(String, primary_key=True, index=True)
    product_id = Column(String, ForeignKey('products.product_id'), index=True)
    warehouse_id = Column(String, ForeignKey(
        'warehouses.warehouse_id'), index=True)
    quantity = Column(Integer)          # Количество данного товара на складе
