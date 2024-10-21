from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from kafka import KafkaConsumer
from . import crud, schemas
from .database import get_db
from .auth import validate_token
import json
from fastapi.security import HTTPBearer


router = APIRouter()

# Создаем объект security для использования схемы авторизации Bearer
security = HTTPBearer()


onsumer = KafkaConsumer('products_topic', bootstrap_servers='localhost:9092',
                        value_deserializer=lambda m: json.loads(m.decode('utf-8')))
