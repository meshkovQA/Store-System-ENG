import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

# ----------------- ЧАТЫ -----------------


class ChatBase(BaseModel):
    name: Optional[str] = None
    is_group: bool = False


class ChatCreate(ChatBase):
    participants: List[uuid.UUID]


class ChatResponse(ChatBase):
    id: uuid.UUID
    created_at: datetime
    participants: List[uuid.UUID]

    class Config:
        from_attributes = True


# ----------------- УЧАСТНИКИ ЧАТА -----------------

class ChatParticipantBase(BaseModel):
    user_id: uuid.UUID
    chat_id: uuid.UUID
    joined_at: datetime

    class Config:
        from_attributes = True


# ----------------- СООБЩЕНИЯ -----------------

class MessageBase(BaseModel):
    chat_id: uuid.UUID
    sender_id: uuid.UUID
    content: str


class MessageCreate(MessageBase):
    pass


class MessageResponse(MessageBase):
    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True
