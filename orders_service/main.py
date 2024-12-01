# main.py

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter
from app import database, logger
from app.kafka import start_consumer
from app.graphql import schema
from app.database import init_db

app = FastAPI(
    title="Order Management Microservice API",
    description="API для управления заказами в системе",
    version="1.0.0"
)

# Добавляем CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Или укажите конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализация базы данных и запуск Kafka-потребителя при старте приложения


@app.on_event("startup")
def startup():
    init_db()
    start_consumer()
    logger.log_message(
        "DB order_service и Kafka consumer initialized successfully")


# Функция для получения контекста
async def get_context(request: Request):
    return {"request": request}

# Создаем GraphQL-приложение
graphql_app = GraphQLRouter(schema, context_getter=get_context)

# Добавляем маршруты для GraphQL-приложения
app.include_router(graphql_app, prefix="/graphql")
