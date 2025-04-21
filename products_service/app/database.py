# database.py
import uuid
from sqlalchemy import Column, String, Boolean, create_engine, Integer, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import SQLALCHEMY_DATABASE_URI

DATABASE_URL = SQLALCHEMY_DATABASE_URI

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def init_db():

    Base.metadata.tables['suppliers'].create(bind=engine, checkfirst=True)
    Base.metadata.tables['products'].create(bind=engine, checkfirst=True)
    Base.metadata.tables['warehouses'].create(bind=engine, checkfirst=True)
    Base.metadata.tables['product_warehouses'].create(
        bind=engine, checkfirst=True)


def get_session_local():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class Supplier(Base):
    __tablename__ = "suppliers"

    supplier_id = Column(UUID(as_uuid=True), primary_key=True,

                         default=uuid.uuid4, unique=True, index=True)
    name = Column(String, index=True)
    contact_name = Column(String)
    contact_email = Column(String)
    phone_number = Column(String)
    address = Column(String)
    country = Column(String)
    city = Column(String)
    website = Column(String)


class Product(Base):
    __tablename__ = "products"

    product_id = Column(UUID(as_uuid=True), primary_key=True,
                        default=uuid.uuid4, unique=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    category = Column(String)
    price = Column(Float)
    stock_quantity = Column(Integer)
    supplier_id = Column(UUID(as_uuid=True), ForeignKey(
        "suppliers.supplier_id"), nullable=False)
    is_available = Column(Boolean)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    weight = Column(Float)
    dimensions = Column(String)
    manufacturer = Column(String)
    image_url = Column(String)
    # ID пользователя, добавившего товар
    user_id = Column(String, nullable=False)


class Warehouse(Base):
    __tablename__ = "warehouses"

    warehouse_id = Column(UUID(as_uuid=True), primary_key=True,
                          default=uuid.uuid4, unique=True, index=True)
    location = Column(String)
    manager_name = Column(String)
    capacity = Column(Integer)
    current_stock = Column(Integer)
    contact_number = Column(String)
    email = Column(String)
    is_active = Column(Boolean)
    area_size = Column(Float)
    created_at = Column(DateTime)


class ProductWarehouse(Base):
    __tablename__ = "product_warehouses"

    product_warehouse_id = Column(UUID(as_uuid=True), primary_key=True,
                                  default=uuid.uuid4, unique=True, index=True)
    product_id = Column(UUID, ForeignKey('products.product_id'), index=True)
    warehouse_id = Column(UUID, ForeignKey(
        'warehouses.warehouse_id'), index=True)
    quantity = Column(Integer)
