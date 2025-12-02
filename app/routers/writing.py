from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.writing import Writing, WritingCreate, WritingUpdate, WritingResponse
from app.auth import get_current_user

router = APIRouter(prefix="/writing", tags=["Writing"])


@router.post("/", response_model=WritingResponse)
async def create_writing(
    writing: WritingCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    db_writing = Writing(**writing.dict())
    db.add(db_writing)
    db.commit()
    db.refresh(db_writing)
    return db_writing


@router.get("/", response_model=List[WritingResponse])
async def get_all_writing(db: Session = Depends(get_db)):
    return db.query(Writing).all()


@router.get("/test/{test_id}", response_model=WritingResponse)
async def get_writing_by_test(test_id: int, db: Session = Depends(get_db)):
    writing = db.query(Writing).filter(Writing.test_id == test_id).first()
    if not writing:
        raise HTTPException(status_code=404, detail="Writing section not found")
    return writing


@router.get("/{writing_id}", response_model=WritingResponse)
async def get_writing(writing_id: int, db: Session = Depends(get_db)):
    writing = db.query(Writing).filter(Writing.id == writing_id).first()
    if not writing:
        raise HTTPException(status_code=404, detail="Writing section not found")
    return writing


@router.put("/{writing_id}", response_model=WritingResponse)
async def update_writing(
    writing_id: int,
    writing_update: WritingUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    writing = db.query(Writing).filter(Writing.id == writing_id).first()
    if not writing:
        raise HTTPException(status_code=404, detail="Writing section not found")
    
    for field, value in writing_update.dict(exclude_unset=True).items():
        setattr(writing, field, value)
    
    db.commit()
    db.refresh(writing)
    return writing


@router.delete("/{writing_id}")
async def delete_writing(
    writing_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    writing = db.query(Writing).filter(Writing.id == writing_id).first()
    if not writing:
        raise HTTPException(status_code=404, detail="Writing section not found")
    
    db.delete(writing)
    db.commit()
    return {"message": "Writing section deleted successfully"}