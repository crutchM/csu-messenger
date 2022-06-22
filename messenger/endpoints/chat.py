"""Методы чата"""


from typing import List

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from core.broker.redis import redis
from deps import get_current_user, get_db
from schemas.chat import ChatInDb, Chat
import crud.chat as crud
import crud.user as cu
import crud.message as cm
from schemas.message import Message
from schemas.user import UserInDB
from schemas.userchat import UserChatInDb, UserChat

router = APIRouter(prefix="/chat")



@router.get("/", response_model=ChatInDb)
async def get_chat(chat_id, user_id=Depends(get_current_user), db=Depends(get_db)):
    """получить по Id"""
    chat = crud.get_by_id(db, chat_id)
    not_found(chat)
    return chat


@router.get("/members", response_model=List[UserInDB])
async def get_chat_members(chat_id, user_id=Depends(get_current_user), db=Depends(get_db)):
    """Все пользователи"""
    members = crud.get_members(db, chat_id)
    not_found(members)
    return members


@router.get("/mychats", response_model=List[ChatInDb])
async def get_my_chats(user=Depends(get_current_user), db=Depends(get_db)):
    """мои чаты"""
    chats = crud.get_all_chats_by_user(db, user)
    not_found(chats)
    return chats

@router.post("/add", response_model=UserChatInDb)
async def add_user(newUser: UserChat, db = Depends(get_db), user =Depends(get_current_user)):
    result = crud.add_user(db, newUser)
    user = cu.get_user_by_id(db, result.user_id)
    msg = cm.create(db, Message(user_id=newUser.user_id, chat_id=newUser.chat_id, text=f"{user.name} join in chat"))
    redis.publish(f"chat-{newUser.chat_id}", msg.text)
    return result




@router.post("/create", response_model=ChatInDb)
async def create_chat(chat: Chat, user=Depends(get_current_user), db=Depends(get_db)):
    """Создать"""
    res = crud.create_chat(db, user, chat)
    return res


def not_found(obj):
    if obj in None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


def forbidden(obj):
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)