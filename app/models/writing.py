from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from typing import Optional
from app.database import Base


class Writing(Base):
    __tablename__ = "ielts_writing"
    
    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("ielts_tests.id"), nullable=False)
    task_1_text = Column(Text, nullable=False)
    task_2_text = Column(Text, nullable=False)
    task_1_image_url = Column(String, nullable=True)
    task_2_image_url = Column(String, nullable=True)
    task_1_instruction = Column(Text, nullable=False)
    task_2_instruction = Column(Text, nullable=False)
    task_1_ai_prompt = Column(Text, nullable=False)
    task_2_ai_prompt = Column(Text, nullable=False)
    
    # Relationship
    test = relationship("Test", back_populates="writing")


# Pydantic Schemas
class WritingCreate(BaseModel):
    test_id: int
    task_1_text: str
    task_2_text: str
    task_1_image_url: Optional[str] = None
    task_2_image_url: Optional[str] = None
    task_1_instruction: str
    task_2_instruction: str
    task_1_ai_prompt: str
    task_2_ai_prompt: str


class WritingUpdate(BaseModel):
    task_1_text: Optional[str] = None
    task_2_text: Optional[str] = None
    task_1_image_url: Optional[str] = None
    task_2_image_url: Optional[str] = None
    task_1_instruction: Optional[str] = None
    task_2_instruction: Optional[str] = None
    task_1_ai_prompt: Optional[str] = None
    task_2_ai_prompt: Optional[str] = None


class WritingResponse(BaseModel):
    id: int
    test_id: int
    task_1_text: str
    task_2_text: str
    task_1_image_url: Optional[str] = None
    task_2_image_url: Optional[str] = None
    task_1_instruction: str
    task_2_instruction: str
    task_1_ai_prompt: str
    task_2_ai_prompt: str
    
    class Config:
        from_attributes = True