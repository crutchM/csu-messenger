import json

from pydantic import BaseModel


class Message(BaseModel):
    user_id: int
    chat_id: int
    text: str

    def convert(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


class MessageInDb(Message):
    id: int

    class Config:
        orm_mode = True


class DatedMessage(Message):
    created: str

    def convert(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)