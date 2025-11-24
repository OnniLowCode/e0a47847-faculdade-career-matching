"""
Student API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from src.config.database import get_db
from src.services.student_service import StudentService
from src.schemas.student import (
    StudentCreate, StudentUpdate, StudentResponse, StudentDetailResponse,
    GradeCreate, GradeResponse
)

router = APIRouter(prefix="/students", tags=["Students"])


@router.post("", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(
    student_data: StudentCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new student account with profile
    
    - **email**: Student's email (will be used for login)
    - **password**: Password for the account
    - **registration_number**: University registration number (unique)
    - **full_name**: Student's full name
    - **course**: Course/major name
    - **semester**: Current semester (1-12)
    """
    service = StudentService(db)
    
    try:
        student = service.create_student(student_data)
        
        # Add email from user for response
        response = StudentResponse.model_validate(student)
        response.email = student.user.email
        response.created_at = student.user.created_at
        
        return response
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("", response_model=List[StudentResponse])
def list_students(
    skip: int = 0,
    limit: int = 100,
    course: Optional[str] = None,
    semester: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    List all students with optional filters
    
    - **course**: Filter by course name
    - **semester**: Filter by semester
    """
    service = StudentService(db)
    students = service.list_students(skip=skip, limit=limit, course=course, semester=semester)
    
    # Add email to responses
    responses = []
    for student in students:
        response = StudentResponse.model_validate(student)
        response.email = student.user.email if student.user else ""
        responses.append(response)
    
    return responses


@router.get("/{student_id}", response_model=StudentDetailResponse)
def get_student(
    student_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed student information including grades
    """
    service = StudentService(db)
    student = service.get_student_by_id(student_id)
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    # Build detailed response
    grades = service.get_student_grades(student_id)
    grade_responses = []
    
    for grade in grades:
        grade_resp = GradeResponse.model_validate(grade)
        if grade.subject:
            grade_resp.subject_name = grade.subject.name
            grade_resp.subject_code = grade.subject.code
        grade_responses.append(grade_resp)
    
    response = StudentDetailResponse.model_validate(student)
    response.email = student.user.email if student.user else ""
    response.created_at = student.user.created_at if student.user else None
    response.grades = grade_responses
    response.total_credits = sum(g.subject.credits for g in grades if g.subject and g.subject.credits)
    
    return response


@router.get("/registration/{registration_number}", response_model=StudentDetailResponse)
def get_student_by_registration(
    registration_number: str,
    db: Session = Depends(get_db)
):
    """
    Get student by registration number
    """
    service = StudentService(db)
    student = service.get_student_by_registration(registration_number)
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    # Build detailed response
    grades = service.get_student_grades(student.id)
    grade_responses = []
    
    for grade in grades:
        grade_resp = GradeResponse.model_validate(grade)
        if grade.subject:
            grade_resp.subject_name = grade.subject.name
            grade_resp.subject_code = grade.subject.code
        grade_responses.append(grade_resp)
    
    response = StudentDetailResponse.model_validate(student)
    response.email = student.user.email if student.user else ""
    response.created_at = student.user.created_at if student.user else None
    response.grades = grade_responses
    response.total_credits = sum(g.subject.credits for g in grades if g.subject and g.subject.credits)
    
    return response


@router.put("/{student_id}", response_model=StudentResponse)
def update_student(
    student_id: int,
    student_data: StudentUpdate,
    db: Session = Depends(get_db)
):
    """
    Update student profile
    """
    service = StudentService(db)
    student = service.update_student(student_id, student_data)
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    response = StudentResponse.model_validate(student)
    response.email = student.user.email if student.user else ""
    response.created_at = student.user.created_at if student.user else None
    
    return response


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(
    student_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a student account
    """
    service = StudentService(db)
    success = service.delete_student(student_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    return None


@router.post("/{student_id}/grades", response_model=GradeResponse, status_code=status.HTTP_201_CREATED)
def add_grade(
    student_id: int,
    grade_data: GradeCreate,
    db: Session = Depends(get_db)
):
    """
    Add or update a grade for a student
    
    - **subject_id**: ID of the subject
    - **grade**: Grade value (0-10)
    - **semester_year**: Semester/year (e.g., "2024.1")
    """
    service = StudentService(db)
    
    # Verify student exists
    student = service.get_student_by_id(student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    try:
        grade = service.add_grade(student_id, grade_data)
        
        # Build response with subject info
        response = GradeResponse.model_validate(grade)
        if grade.subject:
            response.subject_name = grade.subject.name
            response.subject_code = grade.subject.code
        
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{student_id}/grades", response_model=List[GradeResponse])
def get_student_grades(
    student_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all grades for a student
    """
    service = StudentService(db)
    
    # Verify student exists
    student = service.get_student_by_id(student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    grades = service.get_student_grades(student_id)
    
    # Build responses with subject info
    responses = []
    for grade in grades:
        response = GradeResponse.model_validate(grade)
        if grade.subject:
            response.subject_name = grade.subject.name
            response.subject_code = grade.subject.code
        responses.append(response)
    
    return responses


@router.get("/{student_id}/performance")
def get_academic_performance(
    student_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed academic performance metrics and analytics
    
    Returns:
    - GPA
    - Total subjects completed
    - Performance by category
    - Grade distribution
    """
    service = StudentService(db)
    
    # Verify student exists
    student = service.get_student_by_id(student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    performance = service.get_academic_performance(student_id)
    
    return performance
