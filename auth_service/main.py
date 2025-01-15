# main.py
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app import routes, database, logger, crud, kafka
from sqlalchemy.orm import Session
from app.models import User
from app.database import get_session_local
from app.auth import verify_token
import threading
import uuid
import requests
from app.kafka import create_topic_if_not_exists

app = FastAPI(
    # Укажите название вашего микросервиса здесь
    title="User Manager Microservice API",
    # Описание вашего микросервиса
    description="API for managing users and roles in the application",
    version="1.0.0"  # Версия микросервиса
)
# Добавляем схему безопасности OAuth2 с токенами
security = HTTPBearer()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Либо список доменов
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def start_kafka_consumer():
    # Запуск Kafka Consumer в отдельном потоке
    kafka_thread = threading.Thread(
        target=kafka.listen_for_product_approval_requests, daemon=True)
    kafka_thread.start()


templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.on_event("startup")
def startup():
    database.init_db()
    create_topic_if_not_exists('product_topic')
    start_kafka_consumer()
    logger.log_message("Database initialized.")
    logger.log_message("Kafka consumer started.")


app.include_router(routes.router)

# Вспомогательная функция для рендеринга с проверкой роли супер админа


@app.get("/", include_in_schema=False)
def index():
    return RedirectResponse(url="/login", status_code=303)


@app.get("/products", response_class=HTMLResponse, include_in_schema=False)
def get_products_page(request: Request):
    return templates.TemplateResponse("products.html", {"request": request})


@app.get("/suppliers", response_class=HTMLResponse, include_in_schema=False)
def get_suppliers_page(request: Request):
    return templates.TemplateResponse("suppliers.html", {"request": request})


@app.get("/warehouses", response_class=HTMLResponse, include_in_schema=False)
def get_warehouses_page(request: Request):
    return templates.TemplateResponse("warehouses.html", {"request": request})


@app.get("/pending-approval", response_class=HTMLResponse, include_in_schema=False)
async def pending_approval_page(request: Request):
    return templates.TemplateResponse("pending_approval.html", {"request": request})


@app.get("/user-list", response_class=HTMLResponse, include_in_schema=False)
def get_user_list(request: Request):
    return templates.TemplateResponse("userlist.html", {"request": request})


@app.get("/warehouses_detail/{warehouse_id}", response_class=HTMLResponse, include_in_schema=False)
def warehouse_page(
        warehouse_id: str, request: Request):

    # Передаем данные о складе и продуктах в шаблон
    return templates.TemplateResponse("product_in_warehouse.html", {
        "request": request,
        "warehouse": warehouse_id,
    })


# Обновляем OpenAPI-схему для отображения Bearer токена в Swagger UI
@app.get("/openapi.json", include_in_schema=False)
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = app.openapi()
    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            openapi_schema["paths"][path][method]["security"] = [
                {"bearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema


@app.post("/verify-token", include_in_schema=False)
async def verify_token_endpoint(request: Request, db: Session = Depends(get_session_local)):
    try:
        body = await request.json()  # Получаем JSON-данные из тела запроса
        token = body.get("token")  # Извлекаем токен
        if not token:
            raise HTTPException(status_code=422, detail="Token is required")

        payload = verify_token(token, db)
        logger.log_message(f"""Returning from verify_token_endpoint: valid=True, user_id={
                           payload.get('sub')}""")
        return {"valid": True, "user_id": payload.get("sub")}
    except HTTPException as e:
        return {"valid": False, "error": str(e.detail)}


@app.get("/check-superadmin", include_in_schema=False)
async def check_superadmin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_session_local)
):
    token = credentials.credentials
    token_data = verify_token(token, db=db)
    user_id = token_data.get("sub")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {"is_superadmin": user.is_superadmin}
