from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app import schemas, crud, models, auth
from app.database import get_db
from app.logger import logger

router = APIRouter()
security = HTTPBearer()


# ---- Маршрут для создания чата ----
@router.post("/chats/", response_model=schemas.ChatResponse, status_code=status.HTTP_201_CREATED, tags=["Chat Service"], summary="Create a new chat")
async def create_chat(chat_data: schemas.ChatCreate, db: Session = Depends(get_db), credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    user_data = auth.verify_token_in_other_service(
        token, require_admin=True)  # Требуем, чтобы был админ
    user_id = user_data["user_id"]

    if not user_data:
        logger.log_message("Unauthorized access attempt")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid token or unauthorized access")

    # Проверяем, что в чате есть хотя бы два участника
    if len(chat_data.participants) < 2:
        raise HTTPException(
            status_code=400, detail="A chat must have at least two participants")

    # Создание чата
    logger.log_message(f"Admin {user_id} is creating a chat")
    return crud.create_chat(db=db, chat_data=chat_data)


# ---- Маршрут для получения всех чатов пользователя ----
@router.get("/chats/", response_model=List[schemas.ChatResponse], tags=["Chat Service"], summary="Get all user chats")
async def get_user_chats(db: Session = Depends(get_db), credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    user_data = auth.verify_token_in_other_service(token)
    if not user_data:
        logger.log_message("Unauthorized access attempt")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid token or unauthorized access")

    logger.log_message(f"User {user_data} is fetching their chats")
    return crud.get_user_chats(db, user_id=user_data)


# ---- Маршрут для получения сообщений в чате ----
@router.get("/chats/{chat_id}/messages", response_model=List[schemas.MessageResponse], tags=["Chat Service"], summary="Get chat messages")
async def get_chat_messages(chat_id: str, db: Session = Depends(get_db), credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    user_data = auth.verify_token_in_other_service(token)
    if not user_data:
        logger.log_message("Unauthorized access attempt")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid token or unauthorized access")

    # Проверка корректности UUID
    try:
        chat_uuid = UUID(chat_id)
    except ValueError:
        raise HTTPException(
            status_code=400, detail="Invalid UUID format for Chat ID")

    logger.log_message(
        f"User {user_data} is fetching messages for chat {chat_id}")
    return crud.get_chat_messages(db, chat_uuid)


# ---- Маршрут для отправки сообщения ----
@router.post("/chats/{chat_id}/messages", response_model=schemas.MessageResponse, status_code=status.HTTP_201_CREATED, tags=["Chat Service"], summary="Send a message in a chat")
async def send_message(chat_id: str, message_data: schemas.MessageCreate, db: Session = Depends(get_db), credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    user_data = auth.verify_token_in_other_service(token)
    if not user_data:
        logger.log_message("Unauthorized access attempt")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid token or unauthorized access")

    # Проверка корректности UUID
    try:
        chat_uuid = UUID(chat_id)
    except ValueError:
        raise HTTPException(
            status_code=400, detail="Invalid UUID format for Chat ID")

    # Проверка, состоит ли пользователь в чате
    chat = crud.get_chat_by_id(db, chat_uuid)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    if user_data not in [participant.user_id for participant in chat.participants]:
        raise HTTPException(
            status_code=403, detail="User is not a participant of this chat")

    # Создание сообщения
    logger.log_message(
        f"User {user_data} is sending a message in chat {chat_id}")
    return crud.create_message(db=db, message_data=message_data)

# ---- Маршрут для добавления пользователя в чат ----


@router.post("/chats/{chat_id}/add_user", status_code=status.HTTP_200_OK, tags=["Chat Service"], summary="Add a user to a chat")
def add_user_to_chat(chat_id: UUID, user_id: UUID, db: Session = Depends(get_db), credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    user_data = auth.verify_token_in_other_service(
        token, require_admin=True)  # Проверяем, что это админ

    if not user_data:
        logger.log_message("Unauthorized access attempt")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid token or unauthorized access")
    """Добавляет пользователя в чат"""
    chat = crud.get_chat_by_id(db, chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    # Проверяем, состоит ли пользователь уже в чате
    existing_participant = db.query(models.ChatParticipant).filter(
        models.ChatParticipant.chat_id == chat_id,
        models.ChatParticipant.user_id == user_id
    ).first()

    if existing_participant:
        raise HTTPException(status_code=400, detail="User already in chat")

    # Добавляем пользователя в чат
    crud.add_user_to_chat(db, chat_id, user_id)

    logger.log_message(f"""Admin {user_data['user_id']} added user {
                       user_id} to chat {chat_id}""")

    return {"message": "User added to chat successfully"}
