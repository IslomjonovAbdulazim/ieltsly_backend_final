from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.test import Test
from app.models.test import TestCreate, TestUpdate, TestResponse
from app.auth import get_current_user

router = APIRouter(prefix="/tests", tags=["Tests"])


@router.post("/", response_model=TestResponse)
async def create_test(
    test: TestCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    db_test = Test(**test.dict())
    db.add(db_test)
    db.commit()
    db.refresh(db_test)
    return db_test


@router.get("/", response_model=List[TestResponse])
async def get_tests(db: Session = Depends(get_db)):
    return db.query(Test).all()


@router.get("/{test_id}", response_model=TestResponse)
async def get_test(test_id: int, db: Session = Depends(get_db)):
    test = db.query(Test).filter(Test.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    return test


@router.put("/{test_id}", response_model=TestResponse)
async def update_test(
    test_id: int,
    test_update: TestUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    test = db.query(Test).filter(Test.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    for field, value in test_update.dict(exclude_unset=True).items():
        setattr(test, field, value)
    
    db.commit()
    db.refresh(test)
    return test


@router.delete("/{test_id}")
async def delete_test(
    test_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    test = db.query(Test).filter(Test.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    db.delete(test)
    db.commit()
    return {"message": "Test deleted successfully"}