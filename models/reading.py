from pydantic import BaseModel, validator
from typing import List, Optional, Union, Dict
from enum import Enum
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
    question_packs = relationship("DBQuestionPack", back_populates="passage", cascade="all, delete-orphan")


class DBParagraph(Base):
    __tablename__ = "reading_paragraphs"
    
    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    order = Column(Integer, nullable=False)
    label = Column(String(1), nullable=True)
    passage_id = Column(Integer, ForeignKey("reading_passages.id"), nullable=False)
    
    passage = relationship("DBReadingPassage", back_populates="paragraphs")


class QuestionType(str, Enum):
    TRUE_FALSE_NOT_GIVEN = "TRUE_FALSE_NOT_GIVEN"
    YES_NO_NOT_GIVEN = "YES_NO_NOT_GIVEN"
    SUMMARY_COMPLETION = "SUMMARY_COMPLETION"
    SENTENCE_COMPLETION = "SENTENCE_COMPLETION"
    CHOOSE_FROM_BOX = "CHOOSE_FROM_BOX"
    MULTIPLE_CHOICE = "MULTIPLE_CHOICE"
    MCQ_MULTIPLE = "MCQ_MULTIPLE"


class TrueFalseAnswer(str, Enum):
    TRUE = "TRUE"
    FALSE = "FALSE"
    NOT_GIVEN = "NOT_GIVEN"


class YesNoAnswer(str, Enum):
    YES = "YES"
    NO = "NO"
    NOT_GIVEN = "NOT_GIVEN"


class DBQuestionPack(Base):
    __tablename__ = "reading_question_packs"
    
    id = Column(Integer, primary_key=True, index=True)
    passage_id = Column(Integer, ForeignKey("reading_passages.id"), nullable=False)
    type = Column(String, nullable=False)  # QuestionType enum value
    start_question = Column(Integer, nullable=False)
    end_question = Column(Integer, nullable=False)
    
    passage = relationship("DBReadingPassage", back_populates="question_packs")
    questions = relationship("DBQuestion", back_populates="pack", cascade="all, delete-orphan")


class DBQuestion(Base):
    __tablename__ = "reading_questions"
    
    id = Column(Integer, primary_key=True, index=True)
    pack_id = Column(Integer, ForeignKey("reading_question_packs.id"), nullable=False)
    number = Column(Integer, nullable=True)  # Question number within the pack (nullable for MCQ_MULTIPLE)
    title = Column(String, nullable=True)  # Optional title for questions
    text = Column(Text, nullable=False)  # Question text
    options = Column(JSON, nullable=True)  # Multiple choice options (A, B, C, D) or word box for choose from box
    word_count = Column(Integer, nullable=True)  # Maximum words allowed per blank for summary/sentence completion
    number_count = Column(Integer, nullable=True)  # Maximum numbers allowed per blank for summary/sentence completion
    type = Column(String, nullable=False)  # Same as pack type for consistency
    correct_answer = Column(JSON, nullable=True)  # String for T/F, JSON object for Summary/Sentence/Choose from Box Completion, single letter for MCQ
    
    pack = relationship("DBQuestionPack", back_populates="questions")


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


# Question Pack Models
class QuestionPackCreate(BaseModel):
    type: QuestionType
    start_question: int
    end_question: int

    @validator('end_question')
    def validate_end_after_start(cls, v, values):
        if 'start_question' in values and v < values['start_question']:
            raise ValueError('end_question must be greater than or equal to start_question')
        return v


class QuestionPackUpdate(BaseModel):
    type: Optional[QuestionType] = None
    start_question: Optional[int] = None
    end_question: Optional[int] = None


class QuestionPack(BaseModel):
    id: int
    passage_id: int
    type: QuestionType
    start_question: int
    end_question: int


# Unified Question Models
class QuestionCreate(BaseModel):
    number: Optional[int] = None  # Required for MULTIPLE_CHOICE, TRUE_FALSE_NOT_GIVEN, YES_NO_NOT_GIVEN, SENTENCE_COMPLETION. Not used for MCQ_MULTIPLE, CHOOSE_FROM_BOX, SUMMARY_COMPLETION
    title: Optional[str] = None  # Optional title for questions
    text: str
    options: Optional[Dict[str, str]] = None  # Multiple choice options (A, B, C, D) or word box for CHOOSE_FROM_BOX
    word_count: Optional[int] = None  # Maximum words allowed per blank for summary/sentence completion
    number_count: Optional[int] = None  # Maximum numbers allowed per blank for summary/sentence completion
    correct_answer: Optional[Union[str, Dict[str, str], List[str]]] = None  # String for T/F/MCQ, Dict for Summary/Sentence/Choose from Box Completion, List for MCQ_MULTIPLE
    
    @validator('correct_answer')
    def validate_correct_answer(cls, v):
        if v is not None:  # Only validate if provided
            if isinstance(v, str):
                # String validation for T/F, Y/N, and Multiple Choice questions
                tf_yn_answers = ["TRUE", "FALSE", "NOT_GIVEN", "YES", "NO"]
                mcq_answers = ["A", "B", "C", "D"]
                valid_answers = tf_yn_answers + mcq_answers
                if v not in valid_answers:
                    raise ValueError(f'String correct answer must be one of: {", ".join(valid_answers)}')
            elif isinstance(v, list):
                # List validation for MCQ_MULTIPLE questions - flexible validation
                if len(v) != len(set(v)):
                    raise ValueError('List correct answers must not contain duplicates')
                if len(v) == 0:
                    raise ValueError('List correct answers must not be empty')
                # Further validation will happen in API based on provided options
            elif isinstance(v, dict):
                # Dict validation for Summary/Sentence/Choose from Box Completion - just check it's a dict
                pass  # Further validation will happen in API based on pack type
            else:
                raise ValueError('Correct answer must be a string, list, or dictionary')
        return v


class QuestionUpdate(BaseModel):
    number: Optional[int] = None
    title: Optional[str] = None
    text: Optional[str] = None
    options: Optional[Dict[str, str]] = None  # Multiple choice options (A, B, C, D) or word box for CHOOSE_FROM_BOX
    word_count: Optional[int] = None  # Maximum words allowed per blank for summary/sentence completion
    number_count: Optional[int] = None  # Maximum numbers allowed per blank for summary/sentence completion
    correct_answer: Optional[Union[str, Dict[str, str], List[str]]] = None
    
    @validator('correct_answer')
    def validate_correct_answer(cls, v):
        if v is not None:
            if isinstance(v, str):
                tf_yn_answers = ["TRUE", "FALSE", "NOT_GIVEN", "YES", "NO"]
                mcq_answers = ["A", "B", "C", "D"]
                valid_answers = tf_yn_answers + mcq_answers
                if v not in valid_answers:
                    raise ValueError(f'String correct answer must be one of: {", ".join(valid_answers)}')
            elif isinstance(v, list):
                # List validation for MCQ_MULTIPLE questions - flexible validation
                if len(v) != len(set(v)):
                    raise ValueError('List correct answers must not contain duplicates')
                if len(v) == 0:
                    raise ValueError('List correct answers must not be empty')
                # Further validation will happen in API based on provided options
            elif isinstance(v, dict):
                pass  # Further validation will happen in API based on pack type
            else:
                raise ValueError('Correct answer must be a string, list, or dictionary')
        return v


class Question(BaseModel):
    id: int
    pack_id: int
    number: Optional[int] = None  # Nullable for MCQ_MULTIPLE
    title: Optional[str] = None
    text: str
    options: Optional[Dict[str, str]] = None  # Multiple choice options (A, B, C, D) or word box for CHOOSE_FROM_BOX
    word_count: Optional[int] = None  # Maximum words allowed per blank for summary/sentence completion
    number_count: Optional[int] = None  # Maximum numbers allowed per blank for summary/sentence completion
    type: QuestionType
    correct_answer: Union[str, Dict[str, str], List[str]]


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