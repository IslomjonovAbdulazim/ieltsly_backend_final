from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from config import get_db
from models.reading import (
    ReadingTest, ReadingPassage, ReadingPassageCreate, ReadingPassageUpdate,
    DBReadingTest, DBReadingPassage, DBParagraph,
    Paragraph, ParagraphCreate, ParagraphUpdate
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
    
    paragraphs = [Paragraph(id=p.id, text=p.text, order=p.order, label=p.label, passage_id=p.passage_id) for p in sorted(passage.paragraphs, key=lambda x: x.order)]
    
    return ReadingPassage(id=passage.id, title=passage.title, paragraphs=paragraphs)

@router.post("/passages/", response_model=ReadingPassage)
def create_passage(passage: ReadingPassageCreate, db: Session = Depends(get_db), admin: str = Depends(get_admin_user)):
    db_passage = DBReadingPassage(title=passage.title)
    db.add(db_passage)
    db.commit()
    db.refresh(db_passage)
    return ReadingPassage(id=db_passage.id, title=db_passage.title, paragraphs=[])

@router.put("/passages/{passage_id}", response_model=ReadingPassage)
def update_passage(passage_id: int, passage: ReadingPassageUpdate, db: Session = Depends(get_db), admin: str = Depends(get_admin_user)):
    db_passage = db.query(DBReadingPassage).filter(DBReadingPassage.id == passage_id).first()
    if not db_passage:
        raise HTTPException(status_code=404, detail="Passage not found")
    
    if passage.title is not None:
        db_passage.title = passage.title
    
    db.commit()
    db.refresh(db_passage)
    
    paragraphs = [Paragraph(id=p.id, text=p.text, order=p.order, label=p.label, passage_id=p.passage_id) for p in db_passage.paragraphs]
    
    return ReadingPassage(id=db_passage.id, title=db_passage.title, paragraphs=paragraphs)

@router.delete("/passages/{passage_id}")
def delete_passage(passage_id: int, db: Session = Depends(get_db), admin: str = Depends(get_admin_user)):
    db_passage = db.query(DBReadingPassage).filter(DBReadingPassage.id == passage_id).first()
    if not db_passage:
        raise HTTPException(status_code=404, detail="Passage not found")
    
    db.delete(db_passage)
    db.commit()
    return {"message": "Passage deleted successfully"}

# Paragraph Management Endpoints
@router.get("/passages/{passage_id}/paragraphs/", response_model=List[Paragraph])
def get_paragraphs(passage_id: int, db: Session = Depends(get_db)):
    passage = db.query(DBReadingPassage).filter(DBReadingPassage.id == passage_id).first()
    if not passage:
        raise HTTPException(status_code=404, detail="Passage not found")
    
    paragraphs = db.query(DBParagraph).filter(DBParagraph.passage_id == passage_id).order_by(DBParagraph.order).all()
    return [Paragraph(id=p.id, text=p.text, order=p.order, label=p.label, passage_id=p.passage_id) for p in paragraphs]

@router.post("/passages/{passage_id}/paragraphs/", response_model=Paragraph)
def create_paragraph(passage_id: int, paragraph: ParagraphCreate, db: Session = Depends(get_db), admin: str = Depends(get_admin_user)):
    passage = db.query(DBReadingPassage).filter(DBReadingPassage.id == passage_id).first()
    if not passage:
        raise HTTPException(status_code=404, detail="Passage not found")
    
    if paragraph.order is None:
        max_order = db.query(func.max(DBParagraph.order)).filter(DBParagraph.passage_id == passage_id).scalar()
        paragraph.order = (max_order or 0) + 1
    
    label = paragraph.label.upper() if paragraph.label else None
    
    db_paragraph = DBParagraph(
        text=paragraph.text,
        order=paragraph.order,
        label=label,
        passage_id=passage_id
    )
    db.add(db_paragraph)
    db.commit()
    db.refresh(db_paragraph)
    return Paragraph(id=db_paragraph.id, text=db_paragraph.text, order=db_paragraph.order, label=db_paragraph.label, passage_id=db_paragraph.passage_id)

@router.put("/passages/{passage_id}/paragraphs/{paragraph_id}", response_model=Paragraph)
def update_paragraph(passage_id: int, paragraph_id: int, paragraph: ParagraphUpdate, db: Session = Depends(get_db), admin: str = Depends(get_admin_user)):
    db_paragraph = db.query(DBParagraph).filter(
        DBParagraph.id == paragraph_id,
        DBParagraph.passage_id == passage_id
    ).first()
    if not db_paragraph:
        raise HTTPException(status_code=404, detail="Paragraph not found")
    
    if paragraph.text is not None:
        db_paragraph.text = paragraph.text
    if paragraph.order is not None:
        db_paragraph.order = paragraph.order
    if paragraph.label is not None:
        db_paragraph.label = paragraph.label.upper() if paragraph.label else None
    
    db.commit()
    db.refresh(db_paragraph)
    return Paragraph(id=db_paragraph.id, text=db_paragraph.text, order=db_paragraph.order, label=db_paragraph.label, passage_id=db_paragraph.passage_id)

@router.put("/passages/{passage_id}/paragraphs/{paragraph_id}/order")
def update_paragraph_order(passage_id: int, paragraph_id: int, new_order: int, db: Session = Depends(get_db), admin: str = Depends(get_admin_user)):
    db_paragraph = db.query(DBParagraph).filter(
        DBParagraph.id == paragraph_id,
        DBParagraph.passage_id == passage_id
    ).first()
    if not db_paragraph:
        raise HTTPException(status_code=404, detail="Paragraph not found")
    
    old_order = db_paragraph.order
    db_paragraph.order = new_order
    
    if new_order > old_order:
        db.query(DBParagraph).filter(
            DBParagraph.passage_id == passage_id,
            DBParagraph.order > old_order,
            DBParagraph.order <= new_order,
            DBParagraph.id != paragraph_id
        ).update({DBParagraph.order: DBParagraph.order - 1})
    else:
        db.query(DBParagraph).filter(
            DBParagraph.passage_id == passage_id,
            DBParagraph.order >= new_order,
            DBParagraph.order < old_order,
            DBParagraph.id != paragraph_id
        ).update({DBParagraph.order: DBParagraph.order + 1})
    
    db.commit()
    return {"message": "Paragraph order updated successfully"}

@router.delete("/passages/{passage_id}/paragraphs/{paragraph_id}")
def delete_paragraph(passage_id: int, paragraph_id: int, db: Session = Depends(get_db), admin: str = Depends(get_admin_user)):
    db_paragraph = db.query(DBParagraph).filter(
        DBParagraph.id == paragraph_id,
        DBParagraph.passage_id == passage_id
    ).first()
    if not db_paragraph:
        raise HTTPException(status_code=404, detail="Paragraph not found")
    
    deleted_order = db_paragraph.order
    db.delete(db_paragraph)
    
    db.query(DBParagraph).filter(
        DBParagraph.passage_id == passage_id,
        DBParagraph.order > deleted_order
    ).update({DBParagraph.order: DBParagraph.order - 1})
    
    db.commit()
    return {"message": "Paragraph deleted successfully"}

