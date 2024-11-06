# crud.py
from sqlalchemy.orm import Session
from app.models import User, Token
from app.schemas import UserCreate
from app.auth import get_password_hash
import uuid
from app import logger, schemas


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email.lower()).first()


def create_user(db: Session, user: UserCreate, is_superadmin: bool = False):
    hashed_password = get_password_hash(user.password)
    db_user = User(id=uuid.uuid4(), email=user.email,
                   name=user.name, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    logger.log_message(
        f"""A user has been created in the database: {user.email}""")

    # Создаем пользователя в PostgreSQL с ролью limited_user
    assign_role_to_user(db, user.email, user.password)

    return db_user


def assign_role_to_user(db: Session, email: str, password: str):
    # Открываем сырое SQL-соединение, чтобы выполнить SQL-запросы напрямую
    with db.connection().connection.cursor() as cursor:
        # SQL-запрос для создания нового пользователя в PostgreSQL и присвоения ему роли
        create_user_sql = f"""
        CREATE USER "{email}" WITH PASSWORD '{password}';
        GRANT limited_user TO "{email}";
        """
        cursor.execute(create_user_sql)
        db.commit()
        logger.log_message(
            f"A user {email} has been created in PostgreSQL with role limited_user")


def promote_to_superadmin(db: Session, user_id: uuid.UUID):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None

    user.is_superadmin = True
    db.commit()
    db.refresh(user)
    logger.log_message(
        f"A user {user.email} promoted to super admin in the database")
    return user


def get_users_for_superadmin(db: Session):
    return db.query(User).all()


def get_user_by_id(db: Session, user_id: uuid.UUID):
    return db.query(User).filter(User.id == user_id).first()


def edit_user(db: Session, user_id: str, user_data: schemas.UserUpdate):  # Редактирование пользователя
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None

    if user_data.email:
        user.email = user_data.email
    if user_data.name:
        user.name = user_data.name

    # При необходимости можно добавить другие поля для редактирования
    db.commit()
    db.refresh(user)
    logger.log_message(
        f"User {user.email} has been updated in the database")
    return user


def delete_user(db: Session, user_id: str):  # Удаление пользователя
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        # Возвращаем None, если пользователь не найден
        return None

    db.delete(user)
    db.commit()
    logger.log_message(
        f"User {user.email} has been deleted from the database")
    return user


def get_user_token(db: Session, user_id: str):
    return db.query(Token).filter(Token.user_id == user_id).first()
