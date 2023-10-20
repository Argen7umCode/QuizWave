from datetime import datetime
from typing import Any, Optional, List
from sqlmodel import SQLModel, Field, Relationship
from pydantic import BaseModel


class AnswerQuestionLink(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    question_id: Optional[int] = Field(default=None, foreign_key="question.id")
    answer_id: Optional[int] = Field(default=None, foreign_key="answer.id")
    created: datetime 

class Question(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    text: str

    questions: List['Answer'] = Relationship(back_populates='questions', link_model=AnswerQuestionLink)

class Answer(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    text: str

    questions: List[Question] = Relationship(back_populates='questions', link_model=AnswerQuestionLink)




class QuizBlockFromJSerivice(BaseModel):
    id: Optional[int]
    answer: str
    question: str
    value: Optional[int]
    airdate: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    category_id: Optional[int]
    game_id: Optional[int]
    invalid_count: Optional[Any]
    category: Optional[dict]