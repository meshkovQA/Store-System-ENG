# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from app import routes, database, logger, auth
from app.kafka import start_consumer

app = FastAPI(
    title="Warehouse Management Microservice API",
    description="API for managing products and suppliers in the warehouse",
    version="1.0.0"
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


@app.on_event("startup")
def startup():
    database.init_db()
    start_consumer()
    logger.log_message("Database initialized.")


app.include_router(routes.router)


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
