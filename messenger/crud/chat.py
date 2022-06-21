from datetime import datetime
from enum import Enum

from sqlalchemy import and_

import schemas.chat as sc
import schemas.userchat as su
from sqlalchemy.orm import Session

from core.db.models import Chat, UserChat, User


def create_chat(db: Session, user_id:int, chat: sc.Chat):
    chat_db = Chat(name=chat.name, type=chat.type)
    db.add(chat_db)
    db.commit()

    add_user(db, su.UserChat(user_id=user_id, chat_id=chat_db.id))

    return chat_db




def add_user(db: Session, chat_user: su.UserChat):
    user_chat_db = su.UserChat(user_id=chat_user.user_id, chat_id=chat_user.chat_id)
    db.add(user_chat_db)
    db.commit()
    return user_chat_db


def get_by_id(db: Session, chat_id: int):
    return db.query(Chat).filter(Chat.id == chat_id).one_or_none()


def get_chat_by_name(db: Session, name:str):
    return db.query(Chat).filter(Chat.name == name).one_or_none()


def get_userchat(db: Session, user_id: int, chat_id: int):
    return db.query(UserChat).filter(and_(UserChat.chat_id == chat_id, UserChat.user_id == user_id))

def get_members(db: Session, chat_id:int):
    members = db.query(UserChat.user_id).filter(UserChat.chat_id == chat_id).all()
    members = [id[0] for id in members]
    return db.query(User).filter(User.id.in_(members)).all()


def get_all_chats_by_user(db: Session, user_id:int):
    chats = [id[0] for id in (db.query(UserChat.chat_id).filter(UserChat.user_id == user_id).all())]
    return db.query(Chat).filter(Chat.id.in_(chats)).all()


def get_user_from_chat(db: Session, user_id: int, chat_id: int):
    return db.query(UserChat).filter(UserChat.chat_id == chat_id, UserChat.user_id == user_id).first()


def get_row_from_userchat(db: Session, id: int):
    return db.query(UserChat).filter(UserChat.id == id).one_or_none()


def get_al_userchat_by_id(db: Session, id: int):
    return db.query(UserChat).filter(UserChat.chat_id == id)


def update(db: Session, chatid: int, chat: sc.Chat):
    chat_db = db.query(Chat).filter(Chat.id == chatid).one_or_none()
    for p, v in chat.dict().items():
        setattr(chat_db, p, v)
    return chat_db


def delete(db: Session, id: int):
    db.query(Chat).filter(Chat.id == id).delete()
    db.commit()


