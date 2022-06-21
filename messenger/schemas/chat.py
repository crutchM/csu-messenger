from datetime import datetime

from pydantic import BaseModel


class Chat(BaseModel):
    name: str
    type: str


class Created(Chat):
    created_at: datetime


class ChatInDb(Chat):
    id: int

    class Config:
        orm_mode = True
