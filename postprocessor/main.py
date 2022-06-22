from typing import List

from fastapi import FastAPI, Body
import uvicorn

import domain.parsing as domain
from schemas import Extra


app = FastAPI()


@app.post("/extra", response_model=List[Extra])
def get_extra(text: str = Body(..., embed=True)):
    """Получает экстра-данные из текста"""
    return domain.get_extra(text)


@app.get("/process", response_model=str)
def process_text(text: str):
    for extra in get_extra(text):
        if extra['type'] == 'link':
            text = text.replace(extra['text'], f"<a href='{extra['text']}'>{extra['text']}</a>")
        if extra['type'] == 'hashtag':
            text = text.replace(extra['text'], f"<a href='#'>{extra['text']}</a>")
        elif extra['type'] == 'mention':
            text = text.replace(extra['text'],
                                f"<a href='https://t.me/{extra['text'][1:]}' target=\"_blank\">{extra['text']}</a>")
    return text


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host='0.0.0.0',
        port=8080,
        reload=True,
        debug=True,
    )
