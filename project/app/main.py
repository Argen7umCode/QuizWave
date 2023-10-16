from fastapi import Depends, FastAPI
from sqlalchemy import select
from sqlmodel import Session

from app.db import get_session, init_db

import aiohttp

app = FastAPI()







@app.on_event("startup")
def on_startup():
    init_db()


@app.post("/api/qurestions/{questions_num}")
async def get_questions(questions_num: int):
    return 


