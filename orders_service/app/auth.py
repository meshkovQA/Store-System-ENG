# auth.py

import requests
from fastapi import HTTPException, status
from app.config import AUTH_SERVICE_URL
from app import logger


def verify_token_in_other_service(token: str, require_admin: bool = False):
    headers = {"Content-Type": "application/json"}
    response = requests.post(
        f"{AUTH_SERVICE_URL}/verify-token-with-admin", json={"token": token}, headers=headers)
    if response.status_code != 200 or not response.json().get("valid"):
        logger.log_message(
            "Invalid token or unauthorized access")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid token or unauthorized access")
    user_id = response.json().get("user_id")
    is_admin = response.json().get("is_superadmin", False)
    if require_admin and not is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Requires admin access")
    return {"user_id": user_id, "is_superadmin": is_admin}
