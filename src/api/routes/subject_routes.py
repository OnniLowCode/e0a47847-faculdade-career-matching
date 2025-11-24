"""
Subject/Discipline API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from src.config.database import get_db
from src.services.subject_service import SubjectService
from src.schemas.subject import SubjectCreate, SubjectUpdate, SubjectResponse, SubjectWithStats

router = APIRouter(prefix="/subjects", tags=["Subjects"])


@router.post("", response_model=SubjectResponse, status_code=status.HTTP_201_CREATED)
def create_subject(
    subject_data: SubjectCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new subject/discipline
    
    - **code**: Subject code (unique identifier)
    - **name**: Subject name
    - **course**: Course/major this subject belongs to
    - **semester**: Recommended semester (1-12)
    - **credits**: Number of credits
    - **category**: Subject category (e.g., "programming", "mathematics", "business")
    """
    service = SubjectService(db)
    
    try:
        subject = service.create_subject(subject_data)
        return SubjectResponse.model_validate(subject)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/bulk", response_model=List[SubjectResponse])
def create_subjects_bulk(
    subjects_data: List[SubjectCreate],
    db: Session = Depends(get_db)
):
    """
    Create multiple subjects at once
    
    Useful for initial setup or importing curriculum
    """
    service = SubjectService(db)
    subjects = service.bulk_create_subjects(subjects_data)
    
    return [SubjectResponse.model_validate(s) for s in subjects]


@router.get("", response_model=List[SubjectResponse])
def list_subjects(
    skip: int = 0,
    limit: int = 100,
    course: Optional[str] = None,
    semester: Optional[int] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List all subjects with optional filters
    
    - **course**: Filter by course name
    - **semester**: Filter by semester
    - **category**: Filter by category
    """
    service = SubjectService(db)
    subjects = service.list_subjects(
        skip=skip,
        limit=limit,
        course=course,
        semester=semester,
        category=category
    )
    
    return [SubjectResponse.model_validate(s) for s in subjects]


@router.get("/{subject_id}", response_model=SubjectWithStats)
def get_subject(
    subject_id: int,
    db: Session = Depends(get_db)
):
    """
    Get subject details with statistics
    """
    service = SubjectService(db)
    subject = service.get_subject_by_id(subject_id)
    
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found"
        )
    
    # Get statistics
    stats = service.get_subject_statistics(subject_id)
    
    response = SubjectWithStats.model_validate(subject)
    response.total_students = stats.get("total_students", 0)
    response.average_grade = stats.get("average_grade")
    
    return response


@router.get("/code/{subject_code}", response_model=SubjectResponse)
def get_subject_by_code(
    subject_code: str,
    db: Session = Depends(get_db)
):
    """
    Get subject by code
    """
    service = SubjectService(db)
    subject = service.get_subject_by_code(subject_code)
    
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found"
        )
    
    return SubjectResponse.model_validate(subject)


@router.put("/{subject_id}", response_model=SubjectResponse)
def update_subject(
    subject_id: int,
    subject_data: SubjectUpdate,
    db: Session = Depends(get_db)
):
    """
    Update subject information
    """
    service = SubjectService(db)
    subject = service.update_subject(subject_id, subject_data)
    
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found"
        )
    
    return SubjectResponse.model_validate(subject)


@router.delete("/{subject_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subject(
    subject_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a subject
    """
    service = SubjectService(db)
    success = service.delete_subject(subject_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found"
        )
    
    return None


@router.get("/{subject_id}/statistics")
def get_subject_statistics(
    subject_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed statistics for a subject
    
    Returns:
    - Total students enrolled
    - Average grade
    - Highest/lowest grades
    - Grade distribution
    """
    service = SubjectService(db)
    
    # Verify subject exists
    subject = service.get_subject_by_id(subject_id)
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found"
        )
    
    stats = service.get_subject_statistics(subject_id)
    
    return stats
