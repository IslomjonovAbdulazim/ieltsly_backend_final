from pydantic import BaseModel, validator
from typing import List
from sqlalchemy import Column, Integer, String, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from config import Base


class DBReadingTest(Base):
    __tablename__ = "reading_tests"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    passage_ids = Column(JSON, nullable=False)
    question_distribution = Column(JSON, nullable=False)
    time_limit = Column(Integer, default=60)
    
    passages = relationship("DBReadingPassage", back_populates="test")


class DBReadingPassage(Base):
    __tablename__ = "reading_passages"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    paragraphs = Column(JSON, nullable=False)
    labels = Column(JSON, nullable=False)
    test_id = Column(Integer, ForeignKey("reading_tests.id"), nullable=True)
    
    test = relationship("DBReadingTest", back_populates="passages")


class Paragraph(BaseModel):
    index: int
    text: str


class Label(BaseModel):
    letter: str
    paragraph_indexes: List[int]


class ReadingPassage(BaseModel):
    id: int
    title: str
    paragraphs: List[Paragraph]
    labels: List[Label]


class ReadingTest(BaseModel):
    id: int
    title: str
    passage_ids: List[int]
    question_distribution: dict[str, int]
    time_limit: int = 60
    
    @validator('question_distribution')
    def validate_question_distribution(cls, v):
        if v:  # Only validate if not empty
            total_questions = sum(v.values())
            if total_questions == 40:
                # Check for 13, 13, 14 distribution (in any order)
                values = list(v.values())
                values.sort()
                if values != [13, 13, 14]:
                    raise ValueError('Question distribution must be 13, 13, 14 questions per passage')
            elif total_questions > 0:
                raise ValueError(f'Total questions must be 40, got {total_questions}')
        
        return v
    
    @validator('passage_ids')
    def validate_passage_ids(cls, v):
        if len(v) > 3:
            raise ValueError('Cannot have more than 3 passage IDs')
        return v