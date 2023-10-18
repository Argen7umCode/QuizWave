from pprint import pprint
from typing import Annotated, Any, List
from datetime import datetime


from fastapi import Depends, FastAPI
from sqlalchemy import func
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
import aiohttp

from app.db import get_session, init_db
from app.models import Question, Answer, AnswerQuestionLink, QuizBlockFromJSerivice


app = FastAPI()




class Getter:
    pass

class QuestionGetter(Getter):

    @staticmethod
    async def get_by_id(id: int, session: AsyncSession):
        return (await select(Question).get(id)).first()

    @staticmethod
    async def get_by_text(text: str, session: AsyncSession):
        return (await session.execute(select(Question).where(Question.question_text == text))).first()    

class AnswerGetter(Getter):

    @staticmethod
    async def get_by_id(id: int, session: AsyncSession):
        return (await select(Answer).get(id)).first()

    @staticmethod
    async def get_by_text(text: str, session: AsyncSession):
        return (await session.execute(select(Answer).where(Answer.answer_text == text))).first()    


class Creator:
    pass

class AnswerCreator(Creator):
    @staticmethod
    async def create(text: str, session: AsyncSession):
        answer = Answer(answer_text=text)
        with session as sess:
            await sess.add(answer)
            await sess.commit()
        return answer

class QuestionCreator(Creator):
    @staticmethod
    async def create(text: str, session: AsyncSession):
        question = Question(question_text=text)
        with session as sess:
            await sess.add(question)
            await sess.commit()
        return question

class AnswerQuestionLinkCreator(Creator):
    @staticmethod
    async def create(answer: Answer, question: Question, session: AsyncSession):
        answ_quest_link = AnswerQuestionLink(question_id=question.id,
                                             answer_id=answer.id,
                                             created=datetime.now())
        with session as sess:
            await sess.add(answ_quest_link)
            await sess.commit()
        return answ_quest_link


class GetterCreator(Getter, Creator):

    async def get_or_create_if_not_exist(self, text, session: AsyncSession):
        item = await self.get_by_text(text, session)
        if item is None:
            item = self.create(text, session)
        return item

class AnswerGetterCreator(AnswerGetter, AnswerCreator, GetterCreator):
    pass

class QuestionGetterCreator(QuestionGetter, QuestionCreator, GetterCreator):
    pass



async def make_request_to_jservice(questions_num: int):
    async with aiohttp.ClientSession() as client:
        async with client.get(f'https://jservice.io/api/random?count={questions_num}') as resp:
            return await resp.json()    

async def is_quize_block_unique(quiz_block: QuizBlockFromJSerivice,
                                session: AsyncSession):
    query = select(func.count(AnswerQuestionLink.id)).join(Question)\
                                                        .join(Answer)\
                                                        .where(Answer.answer_text == quiz_block.answer and
                                                               Question.question_text == quiz_block.question)
    result = (await session.execute(query)).first()[0]
    print(result)
    return result == 0

async def get_blocks_until_is_not_unique(num: int, session: AsyncSession):
    blocks = await make_request_to_jservice(num)
    counter = 0
    for block in blocks:
        quiz_block=QuizBlockFromJSerivice(**block)
        if await is_quize_block_unique(quiz_block=quiz_block,
                                session=session):
            answer, question = [await instance.get_or_create_if_not_exist(text, session)
                                for instance, text in zip((AnswerGetterCreator(), QuestionGetterCreator()),
                                                           (quiz_block.answer, quiz_block.question))]
            answer_question_link = await AnswerQuestionLinkCreator.create(answer, question, session)
        else:
            counter += 1

    print(counter)
    if counter > 0:
        await get_blocks_until_is_not_unique(counter, session)
    else:
        return answer_question_link

@app.on_event("startup")
async def on_startup():
    await init_db()


@app.post("/api/quize_blocks")
async def post_quize_blocks_in_db(num: int, 
                                  session: AsyncSession = Depends(get_session)):
    return await get_blocks_until_is_not_unique(num, session)