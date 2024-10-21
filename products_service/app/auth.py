# auth.py
from jose import JWTError, jwt
from fastapi import HTTPException, status
from auth_service.app.config import SECRET_KEY
from app import logger

SECRET_KEY = SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logger.log_message(f"Token successfully decoded: {payload}")
        return payload
    except JWTError as e:
        logger.log_message(f"Token decoding failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
