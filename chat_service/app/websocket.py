# websocket.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from typing import Dict
from uuid import UUID
from sqlalchemy.orm import Session
import json

from app import crud, schemas, auth
from app.database import get_db, redis_client
from app.logger import logger
from app.kafka import send_chat_notification

router = APIRouter()

# Хранилище активных WebSocket-соединений
active_connections: Dict[UUID, WebSocket] = {}

# Подключение к Redis
CHAT_HISTORY_KEY = "chat_history"


async def send_message_to_chat(chat_id: UUID, message: dict):
    """Отправка сообщения всем участникам чата"""
    for user_id, websocket in active_connections.items():
        if user_id in message["participants"]:
            await websocket.send_text(json.dumps(message))


@router.websocket("/ws/{chat_id}/{user_id}")
async def websocket_endpoint(websocket: WebSocket, chat_id: str, user_id: str, db: Session = Depends(get_db)):
    """WebSocket-соединение для общения в чате"""
    try:
        chat_uuid = UUID(chat_id)
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")

    # Проверяем, есть ли пользователь в чате
    chat = crud.get_chat_by_id(db, chat_uuid)
    if not chat:
        await websocket.close(code=1008)
        return

    if user_uuid not in [p.user_id for p in chat.participants]:
        await websocket.close(code=1008)
        return

    await websocket.accept()
    active_connections[user_uuid] = websocket

    logger.log_message(f"User {user_uuid} connected to chat {chat_id}")

    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)

            # Создаем сообщение в БД
            new_message = schemas.MessageCreate(
                chat_id=chat_uuid,
                sender_id=user_uuid,
                content=message_data["content"]
            )
            message = crud.create_message(db, new_message)

            # Отправляем уведомление в Kafka
            send_chat_notification(chat_uuid, user_uuid, message.content)

            # Сохраняем сообщение в Redis
            redis_client.lpush(f"{CHAT_HISTORY_KEY}:{chat_id}", json.dumps({
                "id": str(message.id),
                "chat_id": str(chat_uuid),
                "sender_id": str(user_uuid),
                "content": message.content,
                "created_at": message.created_at.isoformat()
            }))

            # Отправляем сообщение всем участникам
            message_response = {
                "id": str(message.id),
                "chat_id": str(chat_uuid),
                "sender_id": str(user_uuid),
                "content": message.content,
                "created_at": message.created_at.isoformat(),
                "participants": [str(p.user_id) for p in chat.participants]
            }
            await send_message_to_chat(chat_uuid, message_response)

    except WebSocketDisconnect:
        logger.log_message(
            f"User {user_uuid} disconnected from chat {chat_id}")
        active_connections.pop(user_uuid, None)
