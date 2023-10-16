from sqlmodel import SQLModel, Field, String


class QuizBlock(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    question_id: str = Field(foreign_key="question.id")
    answer_id: str = Field(foreign_key="answer.id")