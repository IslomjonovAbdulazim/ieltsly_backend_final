from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from config import get_db
from models.reading import (
    ReadingTest, ReadingPassage, DBReadingTest, DBReadingPassage
)
from auth import get_admin_user

router = APIRouter()

# Reading Tests CRUD
@router.get("/tests/", response_model=List[ReadingTest])
def get_all_tests(db: Session = Depends(get_db)):
    tests = db.query(DBReadingTest).all()
    return tests

@router.get("/tests/{test_id}", response_model=ReadingTest)
def get_test(test_id: int, db: Session = Depends(get_db)):
    test = db.query(DBReadingTest).filter(DBReadingTest.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    return test

@router.post("/tests/", response_model=ReadingTest)
def create_test(test: ReadingTest, db: Session = Depends(get_db), admin: str = Depends(get_admin_user)):
    db_test = DBReadingTest(
        title=test.title,
        passage_ids=test.passage_ids,
        question_distribution=test.question_distribution,
        time_limit=test.time_limit
    )
    db.add(db_test)
    db.commit()
    db.refresh(db_test)
    return db_test

@router.put("/tests/{test_id}", response_model=ReadingTest)
def update_test(test_id: int, test: ReadingTest, db: Session = Depends(get_db), admin: str = Depends(get_admin_user)):
    db_test = db.query(DBReadingTest).filter(DBReadingTest.id == test_id).first()
    if not db_test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    db_test.title = test.title
    db_test.passage_ids = test.passage_ids
    db_test.question_distribution = test.question_distribution
    db_test.time_limit = test.time_limit
    
    db.commit()
    db.refresh(db_test)
    return db_test

@router.delete("/tests/{test_id}")
def delete_test(test_id: int, db: Session = Depends(get_db), admin: str = Depends(get_admin_user)):
    db_test = db.query(DBReadingTest).filter(DBReadingTest.id == test_id).first()
    if not db_test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    db.delete(db_test)
    db.commit()
    return {"message": "Test deleted successfully"}

# Reading Passages CRUD
@router.get("/passages/", response_model=List[ReadingPassage])
def get_passages_by_test(test_id: int, db: Session = Depends(get_db)):
    test = db.query(DBReadingTest).filter(DBReadingTest.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    passages = []
    for passage_id in test.passage_ids:
        passage = db.query(DBReadingPassage).filter(DBReadingPassage.id == passage_id).first()
        if passage:
            passages.append(passage)
    
    return passages

@router.get("/passages/{passage_id}", response_model=ReadingPassage)
def get_passage(passage_id: int, db: Session = Depends(get_db)):
    passage = db.query(DBReadingPassage).filter(DBReadingPassage.id == passage_id).first()
    if not passage:
        raise HTTPException(status_code=404, detail="Passage not found")
    return passage

@router.post("/passages/", response_model=ReadingPassage)
def create_passage(passage: ReadingPassage, db: Session = Depends(get_db), admin: str = Depends(get_admin_user)):
    db_passage = DBReadingPassage(
        title=passage.title,
        paragraphs=[p.model_dump() for p in passage.paragraphs],
        labels=[l.model_dump() for l in passage.labels]
    )
    db.add(db_passage)
    db.commit()
    db.refresh(db_passage)
    return db_passage

@router.put("/passages/{passage_id}", response_model=ReadingPassage)
def update_passage(passage_id: int, passage: ReadingPassage, db: Session = Depends(get_db), admin: str = Depends(get_admin_user)):
    db_passage = db.query(DBReadingPassage).filter(DBReadingPassage.id == passage_id).first()
    if not db_passage:
        raise HTTPException(status_code=404, detail="Passage not found")
    
    db_passage.title = passage.title
    db_passage.paragraphs = [p.model_dump() for p in passage.paragraphs]
    db_passage.labels = [l.model_dump() for l in passage.labels]
    
    db.commit()
    db.refresh(db_passage)
    return db_passage

@router.delete("/passages/{passage_id}")
def delete_passage(passage_id: int, db: Session = Depends(get_db), admin: str = Depends(get_admin_user)):
    db_passage = db.query(DBReadingPassage).filter(DBReadingPassage.id == passage_id).first()
    if not db_passage:
        raise HTTPException(status_code=404, detail="Passage not found")
    
    db.delete(db_passage)
    db.commit()
    return {"message": "Passage deleted successfully"}