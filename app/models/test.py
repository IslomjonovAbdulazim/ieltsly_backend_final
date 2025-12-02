from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from typing import Optional
from app.database import Base


class Test(Base):
    __tablename__ = "tests"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    image = Column(String, nullable=True)
    description = Column(Text, nullable=False)
    
    # Relationships
    listening = relationship("Listening", back_populates="test", uselist=False)
    reading = relationship("Reading", back_populates="test", uselist=False)
    speaking = relationship("Speaking", back_populates="test", uselist=False)
    writing = relationship("Writing", back_populates="test", uselist=False)


# Pydantic Schemas
class TestCreate(BaseModel):
    title: str
    image: Optional[str] = None
    description: str


class TestUpdate(BaseModel):
    title: Optional[str] = None
    image: Optional[str] = None
    description: Optional[str] = None


class TestResponse(BaseModel):
    id: int
    title: str
    image: Optional[str] = None
    description: str
    
    class Config:
        from_attributes = True