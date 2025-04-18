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

# Create an instance of HTTPBearer for token authentication
security = HTTPBearer()


# Rendering registration page
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

    # Super admin is created by default
    created_user = crud.create_user(db=db, user=user, is_superadmin=False)
    logger.log_message(f"User is registered: {user.email}")

    # Redirect to login page
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"message": "User successfully created",
                 "user": created_user.email}
    )


# Rendering login page
@router.get("/login/", include_in_schema=False)
def register_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


# Authentication route
@router.post("/login/")
def login_for_access_token(form_data: schemas.Login, db: Session = Depends(database.get_session_local)):
    user = crud.get_user_by_email(db, email=form_data.email)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        logger.log_message(f"""Failed login attempt for email: {
                           form_data.email}""")
        raise HTTPException(
            status_code=400, detail="Invalid email or password")

    # Create access token
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


# Upgrade user to super admin
@router.put("/users/promote/{user_id}")
def promote_user_to_superadmin(user_id: str,
                               db: Session = Depends(get_session_local),
                               credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials

    token_data = auth.verify_token(token)
    requesting_user = crud.get_user_by_email(db, token_data["sub"])

    # Check if the requesting user is a super admin
    if not requesting_user.is_superadmin:
        raise HTTPException(status_code=403, detail="Insufficient rights")

    # Upgrade user to super admin
    user = crud.promote_to_superadmin(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    logger.log_message(f"User {user.email} promoted to super admin.")
    return {"detail": "User successfully promoted to super admin"}


# Get list of users for super admin
@router.get("/users/")
def get_users(db: Session = Depends(get_session_local),
              credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials

    token_data = auth.verify_token(token)
    requesting_user = crud.get_user_by_email(db, token_data["sub"])

    if not requesting_user.is_superadmin:
        raise HTTPException(status_code=403, detail="Insufficient rights")

    # Return list of users
    users = crud.get_users_for_superadmin(db)
    return users


# Edit user details
@router.put("/users/edit/{user_id}")
def edit_user(user_id: str, form_data: schemas.UserUpdate, db: Session = Depends(get_session_local), credentials: HTTPAuthorizationCredentials = Depends(security)):

    token = credentials.credentials
    user_data_from_token = auth.verify_token(token)

    requesting_user = crud.get_user_by_email(db, user_data_from_token["sub"])

    if not requesting_user.is_superadmin:
        raise HTTPException(status_code=403, detail="Insufficient rights")

    user = crud.edit_user(db, user_id, form_data)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    logger.log_message(f"User {user.email} has been updated.")
    return {"detail": "User successfully updated", "user": user}

# Delete user


@router.delete("/users/delete/{user_id}")
def delete_user(user_id: str,
                credentials: HTTPAuthorizationCredentials = Depends(security),
                db: Session = Depends(get_session_local)):

    token = credentials.credentials
    user_data_from_token = auth.verify_token(token)

    requesting_user = crud.get_user_by_email(db, user_data_from_token["sub"])
    if not requesting_user.is_superadmin:
        raise HTTPException(status_code=403, detail="Insufficient rights")

    # Delete user
    user = crud.delete_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    logger.log_message(
        f"Super admin {requesting_user.email} deleted user {user.email}.")
    return {"detail": "User successfully deleted", "user": user.email}
