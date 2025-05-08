# main.py
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app import routes, database, logger, auth
from sqlalchemy.orm import Session
from app.database import get_session_local
from app.crud import get_user_by_email
from app.auth import verify_token

app = FastAPI(
    title="User Manager MS",
    description="API for Auth",
    version="1.0.0"
)

security = HTTPBearer()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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


@app.get("/store", include_in_schema=False, response_class=HTMLResponse)
def dashboard_page(request: Request, credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_session_local)):
    token = credentials.credentials
    user_data = auth.verify_token(token)

    if user_data is None:
        logger.log_message("Token is invalid, access denied to /store.")
        raise HTTPException(status_code=403, detail="Not authorized")

    user = get_user_by_email(db, email=user_data["sub"])
    logger.log_message(f"User {user.email} accessed to /store.")

    return templates.TemplateResponse("store.html", {"request": request, "is_superadmin": user.is_superadmin})


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
