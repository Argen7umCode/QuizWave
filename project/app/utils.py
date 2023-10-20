from typing import Annotated, Any, List
from datetime import datetime
from random import choice


import aiohttp
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from app.models import Question, Answer, AnswerQuestionLink, QuizBlockFromJSerivice


class Getter:

    @staticmethod
    async def get_by_id(id: int, 
                        table: Any, 
                        session: AsyncSession):
        return (await session.execute(select(table).get(id))).fetchall()


class OneTextFieldTableGetter(Getter):
    @staticmethod
    async def get_by_text(text: str, 
                          table: Any, 
                          session: AsyncSession):
        return (await session.execute(select(table).where(table.text == text))).fetchall()  

class QuestionGetter(OneTextFieldTableGetter):

    @staticmethod
    async def get_by_id(id: int, 
                        session: AsyncSession):
        return await Getter.get_by_id(id, Question, session)
    
    @staticmethod
    async def get_by_text(text: str, 
                          session: AsyncSession):
        return (await session.execute(select(Question).where(Question.text == text))).fetchall()

class AnswerGetter(OneTextFieldTableGetter):

    @staticmethod
    async def get_by_id(id: int, 
                        session: AsyncSession):
        return await Getter.get_by_id(id, Answer, session)

    @staticmethod
    async def get_by_text(text: str, 
                          session: AsyncSession):
        return (await session.execute(select(Answer).where(Answer.text == text))).fetchall()


class AnswerQuestionLinkGetter(OneTextFieldTableGetter):

    @staticmethod
    async def get_by_question_text(text: str, 
                                   session: AsyncSession):
        question = (await OneTextFieldTableGetter.get_by_text(text, Question, session)).first()
        query = select(AnswerQuestionLink).join(Question).where(AnswerQuestionLink.question_id==question.id)
        return (await session.execute(query)).fetchall()

    @staticmethod
    async def get_by_question_text(text: str, 
                                   session: AsyncSession):
        answer = (await OneTextFieldTableGetter.get_by_text(text, Answer, session)).first()
        query = select(AnswerQuestionLink).join(Answer).where(AnswerQuestionLink.answer_id==answer.id)
        return (await session.execute(query)).fetchall()
    
    @staticmethod
    async def get_by_question_answer_texts(question_text: str, 
                                           answer_text: str, 
                                           session: AsyncSession):
        query = select(func.count(AnswerQuestionLink.id)).join(Question)\
                                                        .join(Answer)\
                                                        .where(Answer.text == question_text and
                                                               Question.text == answer_text)
        return (await session.execute(query)).fetchall()
    
    @staticmethod
    async def get(session: AsyncSession):
        query = select(AnswerQuestionLink).join(Question)\
                                          .join(Answer)
        print(query)
        return (await session.execute(query)).fetchall()
    
class Creator:

    @staticmethod
    async def create(item: Any, 
                     session: AsyncSession):
        session.add(item)
        await session.commit()
        return item

class AnswerCreator(Creator):
    @staticmethod
    async def create(text: str, 
                     session: AsyncSession):
        answer = Answer(text=text)
        return await Creator.create(answer, session)
    
class QuestionCreator(Creator):
    @staticmethod
    async def create(text: str, 
                     session: AsyncSession):
        question = Question(text=text)
        return await Creator.create(question, session)
    

class AnswerQuestionLinkCreator(Creator):
    @staticmethod
    async def create(answer: Answer, 
                     question: Question, 
                     session: AsyncSession):
        answ_quest_link = AnswerQuestionLink(answer_id=answer.id,
                                             question_id=question.id,
                                             created=datetime.now())
        return await Creator.create(answ_quest_link, session)

class GetterCreator(Getter, Creator):

    async def get_or_create_if_not_exist(self, 
                                         text: str, 
                                         session: AsyncSession):
        item = (await self.get_by_text(text, session))
        if item == []:
            print('true')
            return (await self.create(text, session))
        else: 
            print('false')
            return item[0][0]

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
    result = (await AnswerQuestionLinkGetter.get_by_question_answer_texts(quiz_block.question, 
                                                                   quiz_block.answer,
                                                                   session))[0][0]
    return result == 0

async def get_blocks_until_is_not_unique(num: int, session: AsyncSession):
    blocks = await make_request_to_jservice(num)
    counter = 0
    for block in blocks:
        quiz_block=QuizBlockFromJSerivice(**block)
        if await is_quize_block_unique(quiz_block=quiz_block,
                                session=session):
            answer = (await AnswerGetterCreator().get_or_create_if_not_exist(quiz_block.answer, session))
            question = (await QuestionGetterCreator().get_or_create_if_not_exist(quiz_block.question, session))
            print()
            print(answer)
            print(question)
            print()
            answer_question_link = await AnswerQuestionLinkCreator.create(answer, question, session)
        else:
            counter += 1

    if counter > 0:
        await get_blocks_until_is_not_unique(counter, session)
    else:
        return await get_block_from_db(answer_question_link.id, session)
    

async def get_block_from_db(id: int, session: AsyncSession):
    query = select(Answer.text.label('answer'), Question.text.label('question'), AnswerQuestionLink.created)\
                        .join(Answer).join(Question)\
                        .where(AnswerQuestionLink.id == id)
    return dict((await session.execute(query)).first())
      

async def get_blocks_from_db(num: int, session: AsyncSession):
    max_id = (await session.execute(select(func.max(AnswerQuestionLink.id)))).one()[0]
    ids = [choice(range(max_id+1)) for _ in range(num)]
    print(ids)
    query = select(Answer.text, Question.text, AnswerQuestionLink.created)\
                        .join(Answer).join(Question)\
                        .where(AnswerQuestionLink.id.in_(ids))
    return (await session.execute(query)).all()