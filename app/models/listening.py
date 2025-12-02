from sqlalchemy import Column, Integer, String, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from typing import Dict, Optional
from app.database import Base


class Listening(Base):
    __tablename__ = "ielts_listening"
    
    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("ielts_tests.id"), nullable=False)
    text1 = Column(Text, nullable=False)
    text2 = Column(Text, nullable=False)
    text3 = Column(Text, nullable=False)
    text4 = Column(Text, nullable=False)
    audio_url1 = Column(String, nullable=False)
    audio_url2 = Column(String, nullable=False)
    audio_url3 = Column(String, nullable=False)
    audio_url4 = Column(String, nullable=False)
    # Example: {1: "A", 2: "Animal", 3: "London", 4: "B"}
    answer_sheet1 = Column(JSON, nullable=False)
    # Example: {1: "C", 2: "Doctor", 3: "Tuesday", 4: "A"}
    answer_sheet2 = Column(JSON, nullable=False)
    # Example: {1: "B", 2: "Library", 3: "15", 4: "D"}
    answer_sheet3 = Column(JSON, nullable=False)
    # Example: {1: "D", 2: "Swimming", 3: "Morning", 4: "C"}
    answer_sheet4 = Column(JSON, nullable=False)
    
    # Relationship
    test = relationship("Test", back_populates="listening")


# Pydantic Schemas
class ListeningCreate(BaseModel):
    test_id: int
    text1: str
    text2: str
    text3: str
    text4: str
    audio_url1: str
    audio_url2: str
    audio_url3: str
    audio_url4: str
    answer_sheet1: Dict[int, str]
    answer_sheet2: Dict[int, str]
    answer_sheet3: Dict[int, str]
    answer_sheet4: Dict[int, str]


class ListeningUpdate(BaseModel):
    text1: Optional[str] = None
    text2: Optional[str] = None
    text3: Optional[str] = None
    text4: Optional[str] = None
    audio_url1: Optional[str] = None
    audio_url2: Optional[str] = None
    audio_url3: Optional[str] = None
    audio_url4: Optional[str] = None
    answer_sheet1: Optional[Dict[int, str]] = None
    answer_sheet2: Optional[Dict[int, str]] = None
    answer_sheet3: Optional[Dict[int, str]] = None
    answer_sheet4: Optional[Dict[int, str]] = None


class ListeningResponse(BaseModel):
    id: int
    test_id: int
    text1: str
    text2: str
    text3: str
    text4: str
    audio_url1: str
    audio_url2: str
    audio_url3: str
    audio_url4: str
    answer_sheet1: Dict[int, str]
    answer_sheet2: Dict[int, str]
    answer_sheet3: Dict[int, str]
    answer_sheet4: Dict[int, str]
    
    class Config:
        from_attributes = True