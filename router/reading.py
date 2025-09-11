from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from config import get_db
from models.reading import (
    ReadingTest, ReadingPassage, ReadingPassageCreate, ReadingPassageUpdate,
    DBReadingTest, DBReadingPassage, DBParagraph,
    Paragraph, ParagraphCreate, ParagraphUpdate,
    QuestionPack, QuestionPackCreate, QuestionPackUpdate, DBQuestionPack,
    Question, QuestionCreate, QuestionUpdate, DBQuestion,
    QuestionType
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
    # Validate test exists if test_id is provided
    if passage.test_id:
        test = db.query(DBReadingTest).filter(DBReadingTest.id == passage.test_id).first()
        if not test:
            raise HTTPException(status_code=404, detail="Test not found")
        
        # Check if test already has 3 passages
        current_passage_count = len(test.passage_ids) if test.passage_ids else 0
        if current_passage_count >= 3:
            raise HTTPException(status_code=400, detail="Test already has maximum of 3 passages")
    
    # Create the passage
    db_passage = DBReadingPassage(title=passage.title, test_id=passage.test_id)
    db.add(db_passage)
    db.commit()
    db.refresh(db_passage)
    
    # Update test's passage_ids if test_id is provided
    if passage.test_id:
        test = db.query(DBReadingTest).filter(DBReadingTest.id == passage.test_id).first()
        current_ids = test.passage_ids if test.passage_ids else []
        updated_ids = current_ids + [db_passage.id]
        test.passage_ids = updated_ids
        db.commit()
    
    return ReadingPassage(id=db_passage.id, title=db_passage.title, paragraphs=[])

@router.put("/passages/{passage_id}", response_model=ReadingPassage)
def update_passage(passage_id: int, passage: ReadingPassageUpdate, db: Session = Depends(get_db), admin: str = Depends(get_admin_user)):
    db_passage = db.query(DBReadingPassage).filter(DBReadingPassage.id == passage_id).first()
    if not db_passage:
        raise HTTPException(status_code=404, detail="Passage not found")
    
    # Update title if provided
    if passage.title is not None:
        db_passage.title = passage.title
    
    # Handle test_id assignment/unassignment only if test_id field is explicitly provided
    if 'test_id' in passage.model_fields_set:
        if passage.test_id is not None:
            # Validate new test exists
            new_test = db.query(DBReadingTest).filter(DBReadingTest.id == passage.test_id).first()
            if not new_test:
                raise HTTPException(status_code=404, detail="Test not found")
            
            # Check if new test already has 3 passages (excluding current passage)
            current_passage_count = len([pid for pid in (new_test.passage_ids or []) if pid != passage_id])
            if current_passage_count >= 3:
                raise HTTPException(status_code=400, detail="Test already has maximum of 3 passages")
            
            # Remove passage from current test if assigned
            if db_passage.test_id and db_passage.test_id != passage.test_id:
                old_test = db.query(DBReadingTest).filter(DBReadingTest.id == db_passage.test_id).first()
                if old_test and old_test.passage_ids:
                    old_test.passage_ids = [pid for pid in old_test.passage_ids if pid != passage_id]
            
            # Assign to new test
            db_passage.test_id = passage.test_id
            current_ids = new_test.passage_ids if new_test.passage_ids else []
            if passage_id not in current_ids:
                new_test.passage_ids = current_ids + [passage_id]
        
        else:  # test_id is explicitly None - unassign
            # Remove from current test if assigned
            if db_passage.test_id:
                old_test = db.query(DBReadingTest).filter(DBReadingTest.id == db_passage.test_id).first()
                if old_test and old_test.passage_ids:
                    old_test.passage_ids = [pid for pid in old_test.passage_ids if pid != passage_id]
            
            db_passage.test_id = None
    
    db.commit()
    db.refresh(db_passage)
    
    # Explicitly load paragraphs with proper ordering
    paragraphs = db.query(DBParagraph).filter(DBParagraph.passage_id == passage_id).order_by(DBParagraph.order).all()
    paragraph_list = [Paragraph(id=p.id, text=p.text, order=p.order, label=p.label, passage_id=p.passage_id) for p in paragraphs]
    
    return ReadingPassage(id=db_passage.id, title=db_passage.title, paragraphs=paragraph_list)

@router.delete("/passages/{passage_id}")
def delete_passage(passage_id: int, db: Session = Depends(get_db), admin: str = Depends(get_admin_user)):
    db_passage = db.query(DBReadingPassage).filter(DBReadingPassage.id == passage_id).first()
    if not db_passage:
        raise HTTPException(status_code=404, detail="Passage not found")
    
    # Update test's passage_ids if passage belongs to a test
    if db_passage.test_id:
        test = db.query(DBReadingTest).filter(DBReadingTest.id == db_passage.test_id).first()
        if test and test.passage_ids:
            # Remove the passage_id from test's passage_ids list
            updated_ids = [pid for pid in test.passage_ids if pid != passage_id]
            test.passage_ids = updated_ids
            db.commit()
    
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
    
    label = paragraph.label.upper() if paragraph.label and paragraph.label.strip() else None
    
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
    # Handle label update - check if label field is explicitly provided
    if 'label' in paragraph.model_fields_set:
        db_paragraph.label = paragraph.label.upper() if paragraph.label and paragraph.label.strip() else None
    
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

# Question Pack Management Endpoints
@router.get("/passages/{passage_id}/question-packs/", response_model=List[QuestionPack])
def get_question_packs(passage_id: int, db: Session = Depends(get_db)):
    passage = db.query(DBReadingPassage).filter(DBReadingPassage.id == passage_id).first()
    if not passage:
        raise HTTPException(status_code=404, detail="Passage not found")
    
    packs = db.query(DBQuestionPack).filter(DBQuestionPack.passage_id == passage_id).order_by(DBQuestionPack.start_question).all()
    return [QuestionPack(id=p.id, passage_id=p.passage_id, type=p.type, start_question=p.start_question, end_question=p.end_question) for p in packs]

@router.post("/passages/{passage_id}/question-packs/", response_model=QuestionPack)
def create_question_pack(passage_id: int, pack: QuestionPackCreate, db: Session = Depends(get_db), admin: str = Depends(get_admin_user)):
    passage = db.query(DBReadingPassage).filter(DBReadingPassage.id == passage_id).first()
    if not passage:
        raise HTTPException(status_code=404, detail="Passage not found")
    
    # Check for overlapping question numbers with existing packs
    existing_packs = db.query(DBQuestionPack).filter(DBQuestionPack.passage_id == passage_id).all()
    for existing_pack in existing_packs:
        if not (pack.end_question < existing_pack.start_question or pack.start_question > existing_pack.end_question):
            raise HTTPException(status_code=400, detail=f"Question numbers {pack.start_question}-{pack.end_question} overlap with existing pack {existing_pack.start_question}-{existing_pack.end_question}")
    
    db_pack = DBQuestionPack(
        passage_id=passage_id,
        type=pack.type.value,
        start_question=pack.start_question,
        end_question=pack.end_question
    )
    db.add(db_pack)
    db.commit()
    db.refresh(db_pack)
    return QuestionPack(id=db_pack.id, passage_id=db_pack.passage_id, type=db_pack.type, start_question=db_pack.start_question, end_question=db_pack.end_question)

@router.put("/passages/{passage_id}/question-packs/{pack_id}", response_model=QuestionPack)
def update_question_pack(passage_id: int, pack_id: int, pack: QuestionPackUpdate, db: Session = Depends(get_db), admin: str = Depends(get_admin_user)):
    db_pack = db.query(DBQuestionPack).filter(
        DBQuestionPack.id == pack_id,
        DBQuestionPack.passage_id == passage_id
    ).first()
    if not db_pack:
        raise HTTPException(status_code=404, detail="Question pack not found")
    
    # Validate question range if provided
    start_q = pack.start_question if pack.start_question is not None else db_pack.start_question
    end_q = pack.end_question if pack.end_question is not None else db_pack.end_question
    
    if end_q < start_q:
        raise HTTPException(status_code=400, detail="end_question must be greater than or equal to start_question")
    
    # Check for overlaps with other packs (excluding current pack)
    existing_packs = db.query(DBQuestionPack).filter(
        DBQuestionPack.passage_id == passage_id,
        DBQuestionPack.id != pack_id
    ).all()
    
    for existing_pack in existing_packs:
        if not (end_q < existing_pack.start_question or start_q > existing_pack.end_question):
            raise HTTPException(status_code=400, detail=f"Question numbers {start_q}-{end_q} overlap with existing pack {existing_pack.start_question}-{existing_pack.end_question}")
    
    # Update fields
    if pack.type is not None:
        db_pack.type = pack.type.value
    if pack.start_question is not None:
        db_pack.start_question = pack.start_question
    if pack.end_question is not None:
        db_pack.end_question = pack.end_question
    
    db.commit()
    db.refresh(db_pack)
    return QuestionPack(id=db_pack.id, passage_id=db_pack.passage_id, type=db_pack.type, start_question=db_pack.start_question, end_question=db_pack.end_question)

@router.delete("/passages/{passage_id}/question-packs/{pack_id}")
def delete_question_pack(passage_id: int, pack_id: int, db: Session = Depends(get_db), admin: str = Depends(get_admin_user)):
    db_pack = db.query(DBQuestionPack).filter(
        DBQuestionPack.id == pack_id,
        DBQuestionPack.passage_id == passage_id
    ).first()
    if not db_pack:
        raise HTTPException(status_code=404, detail="Question pack not found")
    
    db.delete(db_pack)
    db.commit()
    return {"message": "Question pack deleted successfully"}

# Unified Questions Endpoints
@router.get("/question-packs/{pack_id}/questions/", response_model=List[Question])
def get_questions(pack_id: int, db: Session = Depends(get_db)):
    pack = db.query(DBQuestionPack).filter(DBQuestionPack.id == pack_id).first()
    if not pack:
        raise HTTPException(status_code=404, detail="Question pack not found")
    
    questions = db.query(DBQuestion).filter(DBQuestion.pack_id == pack_id).order_by(DBQuestion.number).all()
    return [Question(id=q.id, pack_id=q.pack_id, number=q.number, text=q.text, type=q.type, correct_answer=q.correct_answer) for q in questions]

@router.post("/question-packs/{pack_id}/questions/", response_model=Question)
def create_question(pack_id: int, question: QuestionCreate, db: Session = Depends(get_db), admin: str = Depends(get_admin_user)):
    pack = db.query(DBQuestionPack).filter(DBQuestionPack.id == pack_id).first()
    if not pack:
        raise HTTPException(status_code=404, detail="Question pack not found")
    
    # Set default correct answer if not provided
    if question.correct_answer is None:
        # Use NOT_GIVEN as default for both types
        question.correct_answer = "NOT_GIVEN"
    
    # Validate correct answer based on pack type
    if pack.type == "TRUE_FALSE_NOT_GIVEN":
        valid_answers = ["TRUE", "FALSE", "NOT_GIVEN"]
    elif pack.type == "YES_NO_NOT_GIVEN":
        valid_answers = ["YES", "NO", "NOT_GIVEN"]
    else:
        raise HTTPException(status_code=400, detail=f"Unknown question type: {pack.type}")
    
    if question.correct_answer not in valid_answers:
        raise HTTPException(status_code=400, detail=f"For {pack.type} questions, correct answer must be one of: {', '.join(valid_answers)}")
    
    # Validate question number is within pack range
    if question.number < pack.start_question or question.number > pack.end_question:
        raise HTTPException(status_code=400, detail=f"Question number {question.number} is outside pack range {pack.start_question}-{pack.end_question}")
    
    # Check if question number already exists in this pack
    existing = db.query(DBQuestion).filter(
        DBQuestion.pack_id == pack_id,
        DBQuestion.number == question.number
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Question number {question.number} already exists in this pack")
    
    db_question = DBQuestion(
        pack_id=pack_id,
        number=question.number,
        text=question.text,
        type=pack.type,
        correct_answer=question.correct_answer
    )
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    return Question(id=db_question.id, pack_id=db_question.pack_id, number=db_question.number, text=db_question.text, type=db_question.type, correct_answer=db_question.correct_answer)

@router.put("/question-packs/{pack_id}/questions/{question_id}", response_model=Question)
def update_question(pack_id: int, question_id: int, question: QuestionUpdate, db: Session = Depends(get_db), admin: str = Depends(get_admin_user)):
    db_question = db.query(DBQuestion).filter(
        DBQuestion.id == question_id,
        DBQuestion.pack_id == pack_id
    ).first()
    if not db_question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    pack = db.query(DBQuestionPack).filter(DBQuestionPack.id == pack_id).first()
    
    # Validate correct answer if provided
    if question.correct_answer is not None:
        if pack.type == "TRUE_FALSE_NOT_GIVEN":
            valid_answers = ["TRUE", "FALSE", "NOT_GIVEN"]
        elif pack.type == "YES_NO_NOT_GIVEN":
            valid_answers = ["YES", "NO", "NOT_GIVEN"]
        else:
            raise HTTPException(status_code=400, detail=f"Unknown question type: {pack.type}")
        
        if question.correct_answer not in valid_answers:
            raise HTTPException(status_code=400, detail=f"For {pack.type} questions, correct answer must be one of: {', '.join(valid_answers)}")
        
        db_question.correct_answer = question.correct_answer
    
    # Validate new question number if provided
    if question.number is not None:
        if question.number < pack.start_question or question.number > pack.end_question:
            raise HTTPException(status_code=400, detail=f"Question number {question.number} is outside pack range {pack.start_question}-{pack.end_question}")
        
        # Check if new number conflicts with existing questions (excluding current)
        existing = db.query(DBQuestion).filter(
            DBQuestion.pack_id == pack_id,
            DBQuestion.number == question.number,
            DBQuestion.id != question_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail=f"Question number {question.number} already exists in this pack")
        
        db_question.number = question.number
    
    if question.text is not None:
        db_question.text = question.text
    
    db.commit()
    db.refresh(db_question)
    return Question(id=db_question.id, pack_id=db_question.pack_id, number=db_question.number, text=db_question.text, type=db_question.type, correct_answer=db_question.correct_answer)

@router.delete("/question-packs/{pack_id}/questions/{question_id}")
def delete_question(pack_id: int, question_id: int, db: Session = Depends(get_db), admin: str = Depends(get_admin_user)):
    db_question = db.query(DBQuestion).filter(
        DBQuestion.id == question_id,
        DBQuestion.pack_id == pack_id
    ).first()
    if not db_question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    db.delete(db_question)
    db.commit()
    return {"message": "Question deleted successfully"}

