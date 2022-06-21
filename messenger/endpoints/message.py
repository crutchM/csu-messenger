"""методы сообщения"""
import datetime
import threading

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

import crud.message as crud
from core.broker.redis import redis
from deps import get_current_user, get_db
from schemas.message import MessageInDb, DatedMessage
import asyncio

from util import async_query

router = APIRouter(prefix="/message")


@router.get("/", response_model=MessageInDb)
async def get_message(message, user=Depends(get_current_user), db=Depends(get_db)):
    """Получить сообщение"""
    msg = crud.get_by_id(db, message.id)
    not_found(msg)
    return msg

@router.get("/my", response_model=MessageInDb)
async def get_my_messages(user=Depends(get_current_user), db=Depends(get_db)):
    """все сообщения юзера"""
    msg = crud.get_all_by_user(db, user)
    not_found(msg)
    return msg

@router.get("/byChat", response_model=MessageInDb)
async def get_all_in_chat(chat, user=Depends(get_current_user), db=Depends(get_db)):
    """Все сообщения в чате"""
    msg = crud.get_all_in_chat(db, chat)
    not_found(msg)
    return msg


@router.delete("/")
async def delete(message, user=Depends(get_current_user), db=Depends(get_db)):
    """Удаление"""
    msg = crud.get_by_id(db, message)
    forbidden(msg)
    crud.delete(db, message)


mutex = threading.Lock()


@router.put("/")
async def edit(message: MessageInDb, user=Depends(get_current_user), db=Depends(get_db)):
    """Изменение"""
    mutex.acquire()
    message.text = await async_query("http://localhost:8081/process", message.text)
    mutex.release()
    msg = crud.edit(db, message)
    forbidden(msg)
    return msg


@router.post("/sh", response_model=DatedMessage)
async def make_scheduled_message(message: DatedMessage, user=Depends(get_current_user), db=Depends(get_db)):
    """Отправить отложенное сообщение"""
    mutex.acquire()
    message.text = await async_query("http://localhost:8081/process", message.text)
    mutex.release()
    result = crud.create_sheduled_message(db, message)
    while True:
        dif = datetime.datetime.now() - datetime.datetime.strptime(result.created, "%Y-%m-%d %H:%M:%S")
        if dif.seconds <= 30:
            redis.publish(f"chat-{result.chat_id}", result.convert())
            break
    return result


def not_found(obj):
    if obj in None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


def forbidden(obj):
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)