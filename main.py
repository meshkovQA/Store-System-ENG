# main.py
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from app import routes, database, logger, auth
from sqlalchemy.orm import Session
from app.database import get_session_local
from app.crud import get_user_by_email
from app.auth import verify_token

app = FastAPI()
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
def dashboard_page(request: Request, token: dict = Depends(verify_token), db: Session = Depends(get_session_local)):
    if token is None:
        logger.log_message("Token is None, access denied to /store.")
        raise HTTPException(status_code=403, detail="Not authorized")

    user = get_user_by_email(db, email=token["sub"])
    logger.log_message(f"User {user.email} accessed to /store.")

    return templates.TemplateResponse("store.html", {"request": request, "is_superadmin": user.is_superadmin})
