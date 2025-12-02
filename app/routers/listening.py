from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.listening import Listening, ListeningCreate, ListeningUpdate, ListeningResponse
from app.auth import get_current_user

router = APIRouter(prefix="/listening", tags=["Listening"])


@router.post("/", response_model=ListeningResponse)
async def create_listening(
    listening: ListeningCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    db_listening = Listening(**listening.dict())
    db.add(db_listening)
    db.commit()
    db.refresh(db_listening)
    return db_listening


@router.get("/", response_model=List[ListeningResponse])
async def get_all_listening(db: Session = Depends(get_db)):
    return db.query(Listening).all()


@router.get("/test/{test_id}", response_model=ListeningResponse)
async def get_listening_by_test(test_id: int, db: Session = Depends(get_db)):
    listening = db.query(Listening).filter(Listening.test_id == test_id).first()
    if not listening:
        raise HTTPException(status_code=404, detail="Listening section not found")
    return listening


@router.get("/{listening_id}", response_model=ListeningResponse)
async def get_listening(listening_id: int, db: Session = Depends(get_db)):
    listening = db.query(Listening).filter(Listening.id == listening_id).first()
    if not listening:
        raise HTTPException(status_code=404, detail="Listening section not found")
    return listening


@router.put("/{listening_id}", response_model=ListeningResponse)
async def update_listening(
    listening_id: int,
    listening_update: ListeningUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    listening = db.query(Listening).filter(Listening.id == listening_id).first()
    if not listening:
        raise HTTPException(status_code=404, detail="Listening section not found")
    
    for field, value in listening_update.dict(exclude_unset=True).items():
        setattr(listening, field, value)
    
    db.commit()
    db.refresh(listening)
    return listening


@router.delete("/{listening_id}")
async def delete_listening(
    listening_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    listening = db.query(Listening).filter(Listening.id == listening_id).first()
    if not listening:
        raise HTTPException(status_code=404, detail="Listening section not found")
    
    db.delete(listening)
    db.commit()
    return {"message": "Listening section deleted successfully"}