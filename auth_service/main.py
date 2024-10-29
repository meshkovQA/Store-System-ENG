# main.py
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app import routes, database, logger, crud
from sqlalchemy.orm import Session
from app.database import get_session_local
from app.auth import verify_token
import uuid

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

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.on_event("startup")
def startup():
    database.init_db()
    logger.log_message("Database initialized.")


app.include_router(routes.router)


@app.get("/", include_in_schema=False)
def index():
    return RedirectResponse(url="/login", status_code=303)


# Роут для главной страницы личного кабинета
@app.get("/store", include_in_schema=False, response_class=HTMLResponse)
def dashboard_page(request: Request, db: Session = Depends(get_session_local), credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    logger.log_message(f"DB session: {db}")
    logger.log_message(f"Received token for /store access: {token}")

    token_data = verify_token(token, db=db)

    if token_data is None:
        logger.log_message("Token is invalid, access denied to /store.")
        raise HTTPException(status_code=403, detail="Not authorized")

    user = crud.get_user_by_id(
        db, uuid.UUID(token_data["sub"]))
    logger.log_message(f"User {user.email} accessed to /store.")

    return templates.TemplateResponse("store.html", {"request": request, "is_superadmin": user.is_superadmin})


@app.get("/products", response_class=HTMLResponse, include_in_schema=False)
def get_products_page(request: Request):
    return templates.TemplateResponse("products.html", {"request": request})


@app.get("/suppliers", response_class=HTMLResponse, include_in_schema=False)
def get_products_page(request: Request):
    return templates.TemplateResponse("suppliers.html", {"request": request})


@app.get("/warehouses", response_class=HTMLResponse, include_in_schema=False)
def get_products_page(request: Request):
    return templates.TemplateResponse("warehouses.html", {"request": request})


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
        return {"valid": True, "user_id": payload.get("sub")}
    except HTTPException as e:
        return {"valid": False, "error": str(e.detail)}
