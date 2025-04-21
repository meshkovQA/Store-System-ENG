# auth.py
import requests
from fastapi import HTTPException, status
from app.config import SECRET_KEY
from app import logger


AUTH_SERVICE_URL = "http://auth_service:8000/verify-token"


def verify_token_in_other_service(token: str):
    headers = {"Content-Type": "application/json"}
    response = requests.post(AUTH_SERVICE_URL, json={
                             "token": token}, headers=headers)
    logger.log_message(f"Response from auth service: {response.json()}")
    if response.status_code != 200 or not response.json().get("valid"):
        logger.log_message(
            "User ID not found in token data (verify_token_in_other_service)")
        raise HTTPException(
            status_code=401, detail="Invalid token or unauthorized access")

    return response.json().get("user_id")
