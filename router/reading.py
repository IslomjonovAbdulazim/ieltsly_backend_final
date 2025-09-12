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
    
    questions = db.query(DBQuestion).filter(DBQuestion.pack_id == pack_id).order_by(DBQuestion.number.nulls_last()).all()
    return [Question(id=q.id, pack_id=q.pack_id, number=q.number, title=q.title, text=q.text, options=q.options, word_count=q.word_count, number_count=q.number_count, type=q.type, correct_answer=q.correct_answer) for q in questions]

@router.post("/question-packs/{pack_id}/questions/", response_model=Question)
def create_question(pack_id: int, question: QuestionCreate, db: Session = Depends(get_db), admin: str = Depends(get_admin_user)):
    pack = db.query(DBQuestionPack).filter(DBQuestionPack.id == pack_id).first()
    if not pack:
        raise HTTPException(status_code=404, detail="Question pack not found")
    
    # Set default correct answer if not provided
    if question.correct_answer is None:
        if pack.type == "SUMMARY_COMPLETION":
            question.correct_answer = {}  # Empty dict for Summary Completion
        else:
            question.correct_answer = "NOT_GIVEN"  # String for T/F and Y/N
    
    # Validate correct answer based on pack type
    if pack.type == "TRUE_FALSE_NOT_GIVEN":
        valid_answers = ["TRUE", "FALSE", "NOT_GIVEN"]
        if not isinstance(question.correct_answer, str) or question.correct_answer not in valid_answers:
            raise HTTPException(status_code=400, detail=f"For {pack.type} questions, correct answer must be one of: {', '.join(valid_answers)}")
    elif pack.type == "YES_NO_NOT_GIVEN":
        valid_answers = ["YES", "NO", "NOT_GIVEN"]
        if not isinstance(question.correct_answer, str) or question.correct_answer not in valid_answers:
            raise HTTPException(status_code=400, detail=f"For {pack.type} questions, correct answer must be one of: {', '.join(valid_answers)}")
    elif pack.type == "SUMMARY_COMPLETION":
        if not isinstance(question.correct_answer, dict):
            raise HTTPException(status_code=400, detail="For SUMMARY_COMPLETION questions, correct answer must be a dictionary with numbered answers")
        
        # number_count is now for maximum numbers allowed per blank, not total blanks
    elif pack.type == "MULTIPLE_CHOICE":
        if not question.options or not isinstance(question.options, dict):
            raise HTTPException(status_code=400, detail="For MULTIPLE_CHOICE questions, options must be provided as a dictionary")
        
        # Must have exactly A, B, C, D
        required_keys = {"A", "B", "C", "D"}
        if set(question.options.keys()) != required_keys:
            raise HTTPException(status_code=400, detail="For MULTIPLE_CHOICE questions, options must include exactly keys A, B, C, D")
        
        if not isinstance(question.correct_answer, str) or question.correct_answer not in ["A", "B", "C", "D"]:
            raise HTTPException(status_code=400, detail="For MULTIPLE_CHOICE questions, correct answer must be one of: A, B, C, D")
    elif pack.type == "MCQ_MULTIPLE":
        if not question.options or not isinstance(question.options, dict):
            raise HTTPException(status_code=400, detail="For MCQ_MULTIPLE questions, options must be provided as a dictionary")
        
        # Can have A-J (up to 10 options)
        valid_letters = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]
        option_keys = list(question.options.keys())
        
        # Check all keys are valid letters
        invalid_keys = [key for key in option_keys if key not in valid_letters]
        if invalid_keys:
            raise HTTPException(status_code=400, detail=f"For MCQ_MULTIPLE questions, option keys must be letters A-J. Invalid keys: {', '.join(invalid_keys)}")
        
        # Check we have 2 options minimum, maximum based on pack range
        pack_range = pack.end_question - pack.start_question + 1
        max_options = min(10, pack_range)  # Cap at 10, but limited by pack range
        
        if len(option_keys) < 2:
            raise HTTPException(status_code=400, detail="For MCQ_MULTIPLE questions, at least 2 options are required")
        if len(option_keys) > max_options:
            raise HTTPException(status_code=400, detail=f"For MCQ_MULTIPLE questions, maximum {max_options} options allowed (based on pack range {pack.start_question}-{pack.end_question})")
        
        if not isinstance(question.correct_answer, list):
            raise HTTPException(status_code=400, detail="For MCQ_MULTIPLE questions, correct answer must be a list")
        if len(question.correct_answer) == 0:
            raise HTTPException(status_code=400, detail="For MCQ_MULTIPLE questions, at least one correct answer is required")
        if len(question.correct_answer) != len(set(question.correct_answer)):
            raise HTTPException(status_code=400, detail="For MCQ_MULTIPLE questions, correct answers must not contain duplicates")
        
        # Validate all correct answers are valid option keys
        invalid_answers = [ans for ans in question.correct_answer if ans not in option_keys]
        if invalid_answers:
            raise HTTPException(status_code=400, detail=f"For MCQ_MULTIPLE questions, correct answers must be from available options: {', '.join(option_keys)}. Invalid answers: {', '.join(invalid_answers)}")
    else:
        raise HTTPException(status_code=400, detail=f"Unknown question type: {pack.type}")
    
    # Validate question number for non-MCQ_MULTIPLE types
    if pack.type != "MCQ_MULTIPLE":
        if question.number is None:
            raise HTTPException(status_code=400, detail=f"For {pack.type} questions, number field is required")
        
        if question.number < pack.start_question or question.number > pack.end_question:
            raise HTTPException(status_code=400, detail=f"Question number {question.number} is outside pack range {pack.start_question}-{pack.end_question}")
        
        # Check if question number already exists in this pack
        existing = db.query(DBQuestion).filter(
            DBQuestion.pack_id == pack_id,
            DBQuestion.number == question.number
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail=f"Question number {question.number} already exists in this pack")
    else:
        # For MCQ_MULTIPLE, set number to None since it's not used
        question.number = None
    
    db_question = DBQuestion(
        pack_id=pack_id,
        number=question.number,
        title=question.title,
        text=question.text,
        options=question.options,
        word_count=question.word_count,
        number_count=question.number_count,
        type=pack.type,
        correct_answer=question.correct_answer
    )
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    return Question(id=db_question.id, pack_id=db_question.pack_id, number=db_question.number, title=db_question.title, text=db_question.text, options=db_question.options, word_count=db_question.word_count, number_count=db_question.number_count, type=db_question.type, correct_answer=db_question.correct_answer)

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
            if not isinstance(question.correct_answer, str) or question.correct_answer not in valid_answers:
                raise HTTPException(status_code=400, detail=f"For {pack.type} questions, correct answer must be one of: {', '.join(valid_answers)}")
        elif pack.type == "YES_NO_NOT_GIVEN":
            valid_answers = ["YES", "NO", "NOT_GIVEN"]
            if not isinstance(question.correct_answer, str) or question.correct_answer not in valid_answers:
                raise HTTPException(status_code=400, detail=f"For {pack.type} questions, correct answer must be one of: {', '.join(valid_answers)}")
        elif pack.type == "SUMMARY_COMPLETION":
            if not isinstance(question.correct_answer, dict):
                raise HTTPException(status_code=400, detail="For SUMMARY_COMPLETION questions, correct answer must be a dictionary with numbered answers")
            
            # number_count is now for maximum numbers allowed per blank, not total blanks
        elif pack.type == "MULTIPLE_CHOICE":
            if not isinstance(question.correct_answer, str) or question.correct_answer not in ["A", "B", "C", "D"]:
                raise HTTPException(status_code=400, detail="For MULTIPLE_CHOICE questions, correct answer must be one of: A, B, C, D")
        elif pack.type == "MCQ_MULTIPLE":
            if not isinstance(question.correct_answer, list):
                raise HTTPException(status_code=400, detail="For MCQ_MULTIPLE questions, correct answer must be a list")
            if len(question.correct_answer) == 0:
                raise HTTPException(status_code=400, detail="For MCQ_MULTIPLE questions, at least one correct answer is required")
            if len(question.correct_answer) != len(set(question.correct_answer)):
                raise HTTPException(status_code=400, detail="For MCQ_MULTIPLE questions, correct answers must not contain duplicates")
            
            # Get current options or use provided options for validation
            available_options = list((question.options or db_question.options).keys())
            invalid_answers = [ans for ans in question.correct_answer if ans not in available_options]
            if invalid_answers:
                raise HTTPException(status_code=400, detail=f"For MCQ_MULTIPLE questions, correct answers must be from available options: {', '.join(available_options)}. Invalid answers: {', '.join(invalid_answers)}")
        else:
            raise HTTPException(status_code=400, detail=f"Unknown question type: {pack.type}")
        
        db_question.correct_answer = question.correct_answer
    
    # Validate new question number if provided (not for MCQ_MULTIPLE)
    if pack.type != "MCQ_MULTIPLE" and question.number is not None:
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
    elif pack.type == "MCQ_MULTIPLE":
        # For MCQ_MULTIPLE, ignore any provided number and set to None
        db_question.number = None
    
    if question.title is not None:
        db_question.title = question.title
    
    if question.text is not None:
        db_question.text = question.text
    
    if question.options is not None:
        # Validate options for Multiple Choice questions
        if pack.type == "MULTIPLE_CHOICE":
            if not isinstance(question.options, dict):
                raise HTTPException(status_code=400, detail="For MULTIPLE_CHOICE questions, options must be a dictionary")
            required_keys = {"A", "B", "C", "D"}
            if set(question.options.keys()) != required_keys:
                raise HTTPException(status_code=400, detail="For MULTIPLE_CHOICE questions, options must include exactly keys A, B, C, D")
        elif pack.type == "MCQ_MULTIPLE":
            if not isinstance(question.options, dict):
                raise HTTPException(status_code=400, detail="For MCQ_MULTIPLE questions, options must be a dictionary")
            
            valid_letters = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]
            option_keys = list(question.options.keys())
            
            invalid_keys = [key for key in option_keys if key not in valid_letters]
            if invalid_keys:
                raise HTTPException(status_code=400, detail=f"For MCQ_MULTIPLE questions, option keys must be letters A-J. Invalid keys: {', '.join(invalid_keys)}")
            
            pack_range = pack.end_question - pack.start_question + 1
            max_options = min(10, pack_range)
            
            if len(option_keys) < 2:
                raise HTTPException(status_code=400, detail="For MCQ_MULTIPLE questions, at least 2 options are required")
            if len(option_keys) > max_options:
                raise HTTPException(status_code=400, detail=f"For MCQ_MULTIPLE questions, maximum {max_options} options allowed (based on pack range {pack.start_question}-{pack.end_question})")
        
        db_question.options = question.options
    
    if question.word_count is not None:
        db_question.word_count = question.word_count
    
    if question.number_count is not None:
        db_question.number_count = question.number_count
    
    db.commit()
    db.refresh(db_question)
    return Question(id=db_question.id, pack_id=db_question.pack_id, number=db_question.number, title=db_question.title, text=db_question.text, options=db_question.options, word_count=db_question.word_count, number_count=db_question.number_count, type=db_question.type, correct_answer=db_question.correct_answer)

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

