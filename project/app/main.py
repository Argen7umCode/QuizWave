from fastapi import Depends, FastAPI
from sqlalchemy import select
from sqlmodel import Session
import aiohttp


from app.db import get_session, init_db



app = FastAPI()

def 
async def make_request_to_jservice(questions_num: int):
    async with aiohttp.ClientSession() as client:
        async with client.get(f'https://jservice.io/api/random?count={questions_num}') as resp:
            return await resp.json()    


@app.on_event("startup")
def on_startup():
    init_db()


@app.post("/api/qurestions/{questions_num}")
async def get_questions(questions: dict = Depends(make_request_to_jservice)):
    return questions


