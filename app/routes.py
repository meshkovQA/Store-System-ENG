# routes.py
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app import crud, schemas, database, auth, logger
from app.models import User
from fastapi.responses import JSONResponse
from app.database import get_session_local


router = APIRouter()
templates = Jinja2Templates(directory="templates")


# Рендеринг страницы регистрации
@router.get("/register/", include_in_schema=False)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register/", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(database.get_session_local)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        logger.log_message(f"""Registration failed: email {
                           user.email} is already existed.""")
        raise HTTPException(
            status_code=400, detail="Email already registered")

    # Суперадмин не может быть установлен через регистрацию
    created_user = crud.create_user(db=db, user=user, is_superadmin=False)
    logger.log_message(f"User is registered: {user.email}")

    # Перенаправляем на страницу авторизации
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"message": "User successfully created",
                 "user": created_user.email}
    )


# Рендеринг страницы авторизации
@router.get("/login/", include_in_schema=False)
def register_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


# Авторизация пользователя и перенаправление на страницу store
@router.post("/login/")
def login_for_access_token(form_data: schemas.Login, db: Session = Depends(database.get_session_local)):
    user = crud.get_user_by_email(db, email=form_data.email)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        logger.log_message(f"""Failed login attempt for email: {
                           form_data.email}""")
        raise HTTPException(
            status_code=400, detail="Invalid email or password")

    # Создаем access_token
    access_token = auth.create_access_token(
        data={"sub": user.email, "is_superadmin": user.is_superadmin}
    )
    logger.log_message(f"User is logged in: {form_data.email}")
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "User successfully logged in",
                 "access_token": access_token,
                 "token_type": "bearer"}
    )


# Повышение прав до супер-админа (только для супер-админа)
@router.put("/admin/promote/{user_id}")
def promote_user_to_superadmin(user_id: str, db: Session = Depends(database.get_session_local), token: str = Depends(auth.verify_token)):
    # Проверяем, что текущий пользователь является супер-админом
    requesting_user = crud.get_user_by_email(db, email=token["sub"])
    if not requesting_user.is_superadmin:
        raise HTTPException(
            status_code=403, detail="Insufficient rights for promotion")

    user = crud.promote_to_superadmin(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    logger.log_message(f"User {user.email} promoted to super admin.")
    return {"detail": "User successfully promoted to super admin"}


# Получение списка пользователей (только для супер-админа)
@router.get("/users/")
def get_users(request: Request, token: str = Depends(auth.verify_token), db: Session = Depends(get_session_local)):
    # Получаем информацию о пользователе по токену
    requesting_user = crud.get_user_by_email(db, token['sub'])

    # Супер-админ получает доступ ко всем пользователям
    if requesting_user.is_superadmin:
        logger.log_message(
            f"Super admin {requesting_user.email} accessed the user list.")
        users = crud.get_users_for_superadmin(db)
    else:
        # Обычный пользователь видит только свои данные
        logger.log_message(
            f"User {requesting_user.email} accessed their own data.")
        users = [crud.get_user_by_id(db, requesting_user.id, requesting_user)]

    # Проверяем, что запрашивает клиент: HTML или JSON
    if "text/html" in request.headers.get("accept", ""):
        # Если клиент запрашивает HTML, рендерим страницу
        return templates.TemplateResponse("user_list.html", {"request": request, "users": users})
    else:
        # Если клиент запрашивает JSON, возвращаем данные
        return JSONResponse(content={"users": [user.dict() for user in users]})
