from sqlalchemy import Column, Integer, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from typing import List, Optional
from app.database import Base


class Speaking(Base):
    __tablename__ = "speaking"
    
    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("tests.id"), nullable=False)
    # Example: ["Tell me about your hometown", "Describe your favorite hobby", "What are your future plans?"]
    questions = Column(JSON, nullable=False)
    instruction_ai = Column(Text, nullable=False)
    
    # Relationship
    test = relationship("Test", back_populates="speaking")


# Pydantic Schemas
class SpeakingCreate(BaseModel):
    test_id: int
    questions: List[str]
    instruction_ai: str


class SpeakingUpdate(BaseModel):
    questions: Optional[List[str]] = None
    instruction_ai: Optional[str] = None


class SpeakingResponse(BaseModel):
    id: int
    test_id: int
    questions: List[str]
    instruction_ai: str
    
    class Config:
        from_attributes = True