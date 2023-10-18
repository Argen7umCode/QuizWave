from pprint import pprint
from typing import Annotated, Any, List

from fastapi import Depends, FastAPI
from sqlalchemy import func
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
import aiohttp

from app.db import get_session, init_db
from app.models import Question, Answer, AnswerQuestionLink, QuizBlockFromJSerivice


app = FastAPI()


async def is_quize_block_unique(quiz_block: QuizBlockFromJSerivice,
                                session: AsyncSession):
    query = select(func.count(AnswerQuestionLink.id)).join(Question)\
                                                        .join(Answer)\
                                                        .where(Answer.answer_text == quiz_block.answer and
                                                               Question.question_text == quiz_block.question)
    result = await session.execute(query)
    return result == 0

async def create_answer_question(table: Any[Question, Answer], 
                                 text: str, session: AsyncSession):
    row = table(text)
    with session as ses:
        ses.add(row)    
        ses.commit()    

async def get_id_by_text_or_create(text: str, session: AsyncSession):
    

async def create_answer_question(block: QuizBlockFromJSerivice,
                           session: AsyncSession):
    
    query = select(Question.id).where(Question.question_text == block.question)
    question_id = (await session.execute(query)).first()
    if question_id is None:
        question = Question(question_text=block.question)

    query = select(Answer.id).where(Answer.answer_text == block.answer)
    answer_id = (await session.execute(query)).first()
    if answer_id is None:
        answer = Answer(answer_text=block.answer)

async def make_request_to_jservice(questions_num: int):
    async with aiohttp.ClientSession() as client:
        async with client.get(f'https://jservice.io/api/random?count={questions_num}') as resp:
            return await resp.json()    


@app.on_event("startup")
async def on_startup():
    await init_db()


@app.post("/api/quize_blocks")
async def post_quize_blocks_in_db(num: int, 
                                  session: AsyncSession = Depends(get_session)):
    quize_blocks = await make_request_to_jservice(num)
    # print(await is_quize_block_unique(quiz_block=QuizBlockFromJSerivice(**quize_blocks[0]),
    #                             session=session))
    await create_answer_question(QuizBlockFromJSerivice(**quize_blocks[0]), session=session)
    return quize_blocks


