from datetime import datetime

from sqlalchemy import and_
from sqlalchemy.orm import Session

import schemas.message
from core.db.models import UserChat, Message
from crud import chat as cr
from schemas.message import Message, MessageInDb, DatedMessage


def create(db: Session, message: Message):
    if cr.get_user_from_chat(db=db, user_id=message.user_id, chat_id=message.chat_id) is None:
        return False
    message_db = Message(user_chat_id=message.user_chat_id, text=message.text, edited=message.edited, read=message.read)
    db.add(message_db)
    db.commit()
    return schemas.message.MessageInDb(id=message_db.id, user_id=message.user_id, chat_id=message.chat_id,
                                       text=message.text, edited=message_db.edited, read=message_db.read)


def get_by_id(db: Session, id: int):
    message = db.query(Message).filter(Message.id == id).one_or_none()
    pair = cr.get_row_from_userchat(db, id=message.user_chat_id)
    return schemas.message.MessageInDb(id=message.id, user_id=pair.user_id, chat_id=pair.chat_id, text=message.text,
                                       edited=message.edited, read=message.read)


def get_all_by_user(db: Session, id: int):
    chats = cr.get_all_chats_by_user(db=db, user_id=id)
    return db.query(Message).filter(Message.user_chat_id in chats).all()


def delete(db: Session, id: int):
    db.query(Message).filter(Message.id == id).delete()
    db.commit()


def get_all_in_chat(db: Session, chat_id: int, limit: int()):
    chats = cr.get_al_userchat_by_id(db, id=chat_id)
    chats = [uchat.id for uchat in chats]
    query = db.query(Message, UserChat) \
        .filter(
        and_(
            Message.user_chat_id.in_(chats),
            and_(
                Message.created_date < datetime.now()
            )
        )
    ).join(UserChat) \
        .order_by(Message.created_date)

    if (limit > 0):
        result = query.limit(limit).all()
    else:
        result = query.all()

    return [MessageInDb(id=userchat[0].id, user_id=userchat[1].user_id, chat_id=userchat[1].chat_id, text=userchat[0].text,
                                edited=userchat[0].edited, read=userchat[0].read) for userchat in result]


def edit(db: Session, message: MessageInDb):
    message_db = db.query(Message).filter(Message.id == message.id).one_or_none()
    for p, v in message.dict().items():
        setattr(message_db, p, v)
    message_db.edited = True
    db.commit()
    return message_db


def create_sheduled_message(db: Session, message: DatedMessage):
    user_chat: UserChat = cr.get_userchat(db, message.user_id, message.chat_id)
    if user_chat is None:
        return False
    message_db = Message(user_chat_id=user_chat.id, text=message.text, edited=False, read=False,
                         created_date=datetime.strptime(message.created, "%Y-%m-%d %H:%M:%S"), maybesent=False)
    db.add(message_db)
    db.commit()

    return schemas.message.DatedMessage(id=message_db.id, user_id=user_chat.user_id, chat_id=user_chat.chat_id,
                                        text=message_db.text,
                                        edited=message_db.edited, read=message_db.read,
                                        created=str(message_db.created_date))
