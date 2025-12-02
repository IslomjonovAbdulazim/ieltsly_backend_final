from sqlalchemy import Column, Integer, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from typing import Dict, Optional
from app.database import Base


class Reading(Base):
    __tablename__ = "reading"
    
    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("tests.id"), nullable=False)
    text1 = Column(Text, nullable=False)
    text2 = Column(Text, nullable=False)
    text3 = Column(Text, nullable=False)
    text4 = Column(Text, nullable=False)
    # Example: {1: "A", 2: "TRUE", 3: "Climate change", 4: "B"}
    answer_sheet1 = Column(JSON, nullable=False)
    # Example: {1: "C", 2: "FALSE", 3: "Technology", 4: "D"}
    answer_sheet2 = Column(JSON, nullable=False)
    # Example: {1: "B", 2: "NOT GIVEN", 3: "Education", 4: "A"}
    answer_sheet3 = Column(JSON, nullable=False)
    # Example: {1: "D", 2: "TRUE", 3: "Environment", 4: "C"}
    answer_sheet4 = Column(JSON, nullable=False)
    
    # Relationship
    test = relationship("Test", back_populates="reading")


# Pydantic Schemas
class ReadingCreate(BaseModel):
    test_id: int
    text1: str
    text2: str
    text3: str
    text4: str
    answer_sheet1: Dict[int, str]
    answer_sheet2: Dict[int, str]
    answer_sheet3: Dict[int, str]
    answer_sheet4: Dict[int, str]


class ReadingUpdate(BaseModel):
    text1: Optional[str] = None
    text2: Optional[str] = None
    text3: Optional[str] = None
    text4: Optional[str] = None
    answer_sheet1: Optional[Dict[int, str]] = None
    answer_sheet2: Optional[Dict[int, str]] = None
    answer_sheet3: Optional[Dict[int, str]] = None
    answer_sheet4: Optional[Dict[int, str]] = None


class ReadingResponse(BaseModel):
    id: int
    test_id: int
    text1: str
    text2: str
    text3: str
    text4: str
    answer_sheet1: Dict[int, str]
    answer_sheet2: Dict[int, str]
    answer_sheet3: Dict[int, str]
    answer_sheet4: Dict[int, str]
    
    class Config:
        from_attributes = True