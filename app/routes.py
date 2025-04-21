# routes.py
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
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

security = HTTPBearer()


@router.get("/register/", include_in_schema=False)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register/", response_model=schemas.RegistrationResponse, status_code=status.HTTP_201_CREATED, responses={
    201: {"description": "User successfully created", "model": schemas.RegistrationResponse},
    422: {"description": "Email already registered or invalid data"},
})
def register_user(user: schemas.UserCreate, db: Session = Depends(database.get_session_local)):
    user_email = user.email.lower()
    db_user = crud.get_user_by_email(db, email=user_email)
    if db_user:
        logger.log_message(f"""Registration failed: email {
                           user.email} is already existed.""")
        raise HTTPException(
            status_code=422, detail="Email already registered")

    if not user.name.strip():
        raise HTTPException(
            status_code=422, detail="Name contains invalid characters."
        )

    if not user.password.strip():
        raise HTTPException(
            status_code=422, detail="Password contains invalid characters."
        )

    if not user.email.strip():
        raise HTTPException(
            status_code=422, detail="Invalid email format."
        )

    created_user = crud.create_user(db=db, user=user.copy(
        update={"email": user_email}), is_superadmin=False)
    logger.log_message(f"User is registered: {user.email}")

    return JSONResponse(
        content={
            "message": "User successfully created",
            "user_id": str(created_user.id),
            "email": created_user.email,
            "name": created_user.name
        }
    )


@router.get("/login/", include_in_schema=False)
def register_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login/",  response_model=schemas.LoginResponse, responses={
    200: {"description": "User successfully logged in", "model": schemas.LoginResponse},
    400: {"description": "Invalid email or password"}
})
def login_for_access_token(form_data: schemas.Login, db: Session = Depends(database.get_session_local)):
    user = crud.get_user_by_email(db, email=form_data.email)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        logger.log_message(f"""Failed login attempt for email: {
                           form_data.email}""")
        raise HTTPException(
            status_code=400, detail="Invalid email or password")

    access_token = auth.create_access_token(
        data={"sub": user.email, "is_superadmin": user.is_superadmin}
    )
    logger.log_message(f"User is logged in: {form_data.email}")

    return {
        "message": "User successfully logged in",
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.put("/users/promote/{user_id}", status_code=200, responses={
    200: {"description": "User successfully promoted to super admin", "content": {"application/json": {"example": {"detail": "User successfully promoted to super admin"}}}},
    403: {"description": "Insufficient rights", "content": {"application/json": {"example": {"detail": "Insufficient rights"}}}},
    404: {"description": "User not found", "content": {"application/json": {"example": {"detail": "User not found"}}}},
    422: {"description": "This user is already a super admin", "content": {"application/json": {"example": {"detail": "This user is already a super admin"}}}},
})
def promote_user_to_superadmin(user_id: str,
                               db: Session = Depends(get_session_local),
                               credentials: HTTPAuthorizationCredentials = Depends(security)):

    token = credentials.credentials

    token_data = auth.verify_token(token)
    requesting_user = crud.get_user_by_email(db, token_data["sub"])

    if not requesting_user.is_superadmin:
        raise HTTPException(status_code=403, detail="Insufficient rights")

    user = crud.promote_to_superadmin(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.is_superadmin:
        raise HTTPException(
            status_code=422, detail="This user is already a super admin")

    logger.log_message(f"User {user.email} promoted to super admin.")
    return {"detail": "User successfully promoted to super admin"}


@router.get("/users/", response_model=list[schemas.UserResponse])
def get_users(db: Session = Depends(get_session_local),
              credentials: HTTPAuthorizationCredentials = Depends(security)):

    token = credentials.credentials

    token_data = auth.verify_token(token)
    requesting_user = crud.get_user_by_email(db, token_data["sub"])

    if requesting_user.is_superadmin:

        users = crud.get_users_for_superadmin(db)
    else:

        users = [requesting_user]

    result = []
    for user in users:
        result.append({
            "id": str(user.id),
            "name": user.name,
            "email": user.email,
            "role": "superadmin" if user.is_superadmin else "user"
        })

    return result


@router.put("/users/edit/{user_id}", response_model=schemas.UserUpdateResponse, responses={
    200: {"description": "User successfully updated", "model": schemas.UserUpdateResponse},
    403: {"description": "Insufficient rights", "content": {"application/json": {"example": {"detail": "Insufficient rights"}}}},
    404: {"description": "User not found", "content": {"application/json": {"example": {"detail": "User not found"}}}},
})
def edit_user(user_id: str, form_data: schemas.UserUpdate, db: Session = Depends(get_session_local), credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:

        token = credentials.credentials
        user_data_from_token = auth.verify_token(token)

        requesting_user = crud.get_user_by_email(
            db, user_data_from_token["sub"])

        if not requesting_user.is_superadmin:
            raise HTTPException(status_code=403, detail="Insufficient rights")

        user = crud.edit_user(db, user_id, form_data)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        logger.log_message(f"User {user.email} has been updated.")

        return {
            "detail": "User successfully updated",
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email
            }
        }
    except Exception as e:
        logger.log_message(f"An error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.delete("/users/delete/{user_id}", responses={
    200: {"description": "User successfully deleted", "content": {"application/json": {"example": {"detail": "User successfully deleted"}}}},
    403: {"description": "Insufficient rights or attempt to delete own account", "content": {"application/json": {"example": {"detail": "Insufficient rights"}}}},
    404: {"description": "User not found", "content": {"application/json": {"example": {"detail": "User not found"}}}},
})
def delete_user(user_id: str,
                credentials: HTTPAuthorizationCredentials = Depends(security),
                db: Session = Depends(get_session_local)):
    token = credentials.credentials
    user_data_from_token = auth.verify_token(token)

    requesting_user = crud.get_user_by_email(db, user_data_from_token["sub"])
    if not requesting_user.is_superadmin:
        raise HTTPException(status_code=403, detail="Insufficient rights")

    if str(requesting_user.id) == user_id:
        raise HTTPException(
            status_code=403, detail="Super admin cannot delete own account")

    user = crud.delete_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    logger.log_message(
        f"Super admin {requesting_user.email} deleted user {user.email}.")
    return {"detail": "User successfully deleted"}
