from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.speaking import Speaking, SpeakingCreate, SpeakingUpdate, SpeakingResponse
from app.auth import get_current_user

router = APIRouter(prefix="/speaking", tags=["Speaking"])


@router.post("/", response_model=SpeakingResponse)
async def create_speaking(
    speaking: SpeakingCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    db_speaking = Speaking(**speaking.dict())
    db.add(db_speaking)
    db.commit()
    db.refresh(db_speaking)
    return db_speaking


@router.get("/", response_model=List[SpeakingResponse])
async def get_all_speaking(db: Session = Depends(get_db)):
    return db.query(Speaking).all()


@router.get("/test/{test_id}", response_model=SpeakingResponse)
async def get_speaking_by_test(test_id: int, db: Session = Depends(get_db)):
    speaking = db.query(Speaking).filter(Speaking.test_id == test_id).first()
    if not speaking:
        raise HTTPException(status_code=404, detail="Speaking section not found")
    return speaking


@router.get("/{speaking_id}", response_model=SpeakingResponse)
async def get_speaking(speaking_id: int, db: Session = Depends(get_db)):
    speaking = db.query(Speaking).filter(Speaking.id == speaking_id).first()
    if not speaking:
        raise HTTPException(status_code=404, detail="Speaking section not found")
    return speaking


@router.put("/{speaking_id}", response_model=SpeakingResponse)
async def update_speaking(
    speaking_id: int,
    speaking_update: SpeakingUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    speaking = db.query(Speaking).filter(Speaking.id == speaking_id).first()
    if not speaking:
        raise HTTPException(status_code=404, detail="Speaking section not found")
    
    for field, value in speaking_update.dict(exclude_unset=True).items():
        setattr(speaking, field, value)
    
    db.commit()
    db.refresh(speaking)
    return speaking


@router.delete("/{speaking_id}")
async def delete_speaking(
    speaking_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    speaking = db.query(Speaking).filter(Speaking.id == speaking_id).first()
    if not speaking:
        raise HTTPException(status_code=404, detail="Speaking section not found")
    
    db.delete(speaking)
    db.commit()
    return {"message": "Speaking section deleted successfully"}