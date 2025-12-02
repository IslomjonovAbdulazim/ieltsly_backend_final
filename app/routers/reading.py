from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.reading import Reading, ReadingCreate, ReadingUpdate, ReadingResponse
from app.auth import get_current_user

router = APIRouter(prefix="/reading", tags=["Reading"])


@router.post("/", response_model=ReadingResponse)
async def create_reading(
    reading: ReadingCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    db_reading = Reading(**reading.dict())
    db.add(db_reading)
    db.commit()
    db.refresh(db_reading)
    return db_reading


@router.get("/", response_model=List[ReadingResponse])
async def get_all_reading(db: Session = Depends(get_db)):
    return db.query(Reading).all()


@router.get("/test/{test_id}", response_model=ReadingResponse)
async def get_reading_by_test(test_id: int, db: Session = Depends(get_db)):
    reading = db.query(Reading).filter(Reading.test_id == test_id).first()
    if not reading:
        raise HTTPException(status_code=404, detail="Reading section not found")
    return reading


@router.get("/{reading_id}", response_model=ReadingResponse)
async def get_reading(reading_id: int, db: Session = Depends(get_db)):
    reading = db.query(Reading).filter(Reading.id == reading_id).first()
    if not reading:
        raise HTTPException(status_code=404, detail="Reading section not found")
    return reading


@router.put("/{reading_id}", response_model=ReadingResponse)
async def update_reading(
    reading_id: int,
    reading_update: ReadingUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    reading = db.query(Reading).filter(Reading.id == reading_id).first()
    if not reading:
        raise HTTPException(status_code=404, detail="Reading section not found")
    
    for field, value in reading_update.dict(exclude_unset=True).items():
        setattr(reading, field, value)
    
    db.commit()
    db.refresh(reading)
    return reading


@router.delete("/{reading_id}")
async def delete_reading(
    reading_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    reading = db.query(Reading).filter(Reading.id == reading_id).first()
    if not reading:
        raise HTTPException(status_code=404, detail="Reading section not found")
    
    db.delete(reading)
    db.commit()
    return {"message": "Reading section deleted successfully"}