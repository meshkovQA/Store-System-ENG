# auth.py
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import Request
from passlib.context import CryptContext
from config import SECRET_KEY
from app import logger

SECRET_KEY = SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    logger.log_message(f"Created token for: {data.get('sub')}")
    return encoded_jwt


def verify_token(request: Request):
    auth_header = request.headers.get("Authorization")
    if auth_header is None:
        logger.log_message("Authorization header is missing.")
        return None

    try:
        scheme, token = auth_header.split()
        if scheme.lower() != 'bearer':
            logger.log_message(f"Incorrect token scheme: {scheme}")
            return None

        logger.log_message(f"Token received: {token}")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logger.log_message(f"Token successfully decoded: {payload}")
        return payload
    except (JWTError, ValueError) as e:
        logger.log_message(f"Token decoding failed: {str(e)}")
        return None


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)
