from sqlalchemy.orm import Session
import uuid
from datetime import datetime
from app import models, schemas

# ----------------- ЧАТЫ -----------------


def create_chat(db: Session, chat_data: schemas.ChatCreate):
    """Создает новый чат и добавляет участников"""
    chat = models.Chat(id=uuid.uuid4(), name=chat_data.name,
                       is_group=chat_data.is_group)
    db.add(chat)
    db.commit()
    db.refresh(chat)

    # Добавляем участников
    for user_id in chat_data.participants:
        participant = models.ChatParticipant(
            chat_id=chat.id, user_id=user_id, joined_at=datetime.utcnow())
        db.add(participant)

    db.commit()
    return chat


def get_chat_by_id(db: Session, chat_id: uuid.UUID):
    """Получает чат по ID"""
    return db.query(models.Chat).filter(models.Chat.id == chat_id).first()


def get_user_chats(db: Session, user_id: uuid.UUID):
    """Возвращает список чатов, в которых состоит пользователь"""
    return db.query(models.Chat).join(models.ChatParticipant).filter(models.ChatParticipant.user_id == user_id).all()

# ----------------- СООБЩЕНИЯ -----------------


def create_message(db: Session, message_data: schemas.MessageCreate):
    """Создает новое сообщение в чате"""
    message = models.Message(
        id=uuid.uuid4(),
        chat_id=message_data.chat_id,
        sender_id=message_data.sender_id,
        content=message_data.content,
        created_at=datetime.utcnow()
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def get_chat_messages(db: Session, chat_id: uuid.UUID, limit: int = 50):
    """Получает последние N сообщений в чате"""
    return db.query(models.Message).filter(models.Message.chat_id == chat_id).order_by(models.Message.created_at.desc()).limit(limit).all()


def add_user_to_chat(db: Session, chat_id: uuid.UUID, user_id: uuid.UUID):
    """Добавляет пользователя в чат"""
    new_participant = models.ChatParticipant(chat_id=chat_id, user_id=user_id)
    db.add(new_participant)
    db.commit()
    return new_participant
