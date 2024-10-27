# auth.py
from datetime import datetime
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.config import SECRET_KEY
from app import logger
from app.models import Token

SECRET_KEY = SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict, db: Session):
    user_id = data.get("sub")

    # Удаляем старый токен для пользователя
    db.query(Token).filter(Token.user_id == user_id).delete()
    db.commit()

    # Генерируем и сохраняем новый токен
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    new_token = Token(
        token=encoded_jwt,
        user_id=user_id,
        expires_at=expire  # Заполняем время истечения токена
    )
    db.add(new_token)
    db.commit()

    logger.log_message(f"Created new token for: {user_id}")
    return encoded_jwt


def verify_token(token: str, db: Session):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")

        # Проверяем, что токен активен, существует и не истек
        token_record = db.query(Token).filter(
            Token.user_id == user_id, Token.token == token).first()
        if not token_record or token_record.expires_at < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Inactive, expired, or invalid token"
            )

        logger.log_message(
            f"Token successfully decoded and verified: {payload}")
        return payload

    except JWTError as e:
        logger.log_message(f"Token decoding failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)
