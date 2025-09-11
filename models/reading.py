from pydantic import BaseModel, validator
from typing import List, Optional
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
    test_id = Column(Integer, ForeignKey("reading_tests.id"), nullable=True)
    
    test = relationship("DBReadingTest", back_populates="passages")
    paragraphs = relationship("DBParagraph", back_populates="passage", cascade="all, delete-orphan")


class DBParagraph(Base):
    __tablename__ = "paragraphs"
    
    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    order = Column(Integer, nullable=False)
    label = Column(String(1), nullable=True)
    passage_id = Column(Integer, ForeignKey("reading_passages.id"), nullable=False)
    
    passage = relationship("DBReadingPassage", back_populates="paragraphs")


class ParagraphCreate(BaseModel):
    text: str
    order: Optional[int] = None
    label: Optional[str] = None


class ParagraphUpdate(BaseModel):
    text: Optional[str] = None
    order: Optional[int] = None
    label: Optional[str] = None


class Paragraph(BaseModel):
    id: int
    text: str
    order: int
    label: Optional[str] = None
    passage_id: int


class ReadingPassageCreate(BaseModel):
    title: str
    test_id: Optional[int] = None


class ReadingPassageUpdate(BaseModel):
    title: Optional[str] = None
    test_id: Optional[int] = None


class ReadingPassage(BaseModel):
    id: int
    title: str
    paragraphs: List[Paragraph] = []


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