"""
Subject Service - Business logic for subject/discipline operations
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from src.models.models import Subject, Grade
from src.schemas.subject import SubjectCreate, SubjectUpdate


class SubjectService:
    """Service for subject/discipline operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_subject(self, subject_data: SubjectCreate) -> Subject:
        """Create a new subject"""
        # Check if code already exists
        existing = self.db.query(Subject).filter(
            Subject.code == subject_data.code
        ).first()
        
        if existing:
            raise ValueError(f"Subject with code '{subject_data.code}' already exists")
        
        subject = Subject(
            code=subject_data.code,
            name=subject_data.name,
            course=subject_data.course,
            semester=subject_data.semester,
            credits=subject_data.credits,
            description=subject_data.description,
            category=subject_data.category
        )
        self.db.add(subject)
        self.db.commit()
        self.db.refresh(subject)
        
        return subject
    
    def get_subject_by_id(self, subject_id: int) -> Optional[Subject]:
        """Get subject by ID"""
        return self.db.query(Subject).filter(Subject.id == subject_id).first()
    
    def get_subject_by_code(self, code: str) -> Optional[Subject]:
        """Get subject by code"""
        return self.db.query(Subject).filter(Subject.code == code).first()
    
    def list_subjects(
        self,
        skip: int = 0,
        limit: int = 100,
        course: Optional[str] = None,
        semester: Optional[int] = None,
        category: Optional[str] = None
    ) -> List[Subject]:
        """List subjects with filters"""
        query = self.db.query(Subject)
        
        if course:
            query = query.filter(Subject.course == course)
        
        if semester:
            query = query.filter(Subject.semester == semester)
        
        if category:
            query = query.filter(Subject.category == category)
        
        return query.offset(skip).limit(limit).all()
    
    def update_subject(
        self, 
        subject_id: int, 
        subject_data: SubjectUpdate
    ) -> Optional[Subject]:
        """Update subject"""
        subject = self.get_subject_by_id(subject_id)
        
        if not subject:
            return None
        
        update_data = subject_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(subject, field, value)
        
        self.db.commit()
        self.db.refresh(subject)
        
        return subject
    
    def delete_subject(self, subject_id: int) -> bool:
        """Delete a subject"""
        subject = self.get_subject_by_id(subject_id)
        
        if not subject:
            return False
        
        self.db.delete(subject)
        self.db.commit()
        
        return True
    
    def get_subject_statistics(self, subject_id: int) -> dict:
        """Get statistics for a subject"""
        subject = self.get_subject_by_id(subject_id)
        
        if not subject:
            return {}
        
        # Get all grades for this subject
        grades = self.db.query(Grade).filter(
            Grade.subject_id == subject_id
        ).all()
        
        if not grades:
            return {
                "subject_id": subject_id,
                "subject_code": subject.code,
                "subject_name": subject.name,
                "total_students": 0,
                "average_grade": None,
                "highest_grade": None,
                "lowest_grade": None
            }
        
        grade_values = [g.grade for g in grades]
        
        return {
            "subject_id": subject_id,
            "subject_code": subject.code,
            "subject_name": subject.name,
            "total_students": len(grades),
            "average_grade": round(sum(grade_values) / len(grade_values), 2),
            "highest_grade": max(grade_values),
            "lowest_grade": min(grade_values),
            "distribution": {
                "excellent (9-10)": len([g for g in grade_values if g >= 9]),
                "good (7-8.9)": len([g for g in grade_values if 7 <= g < 9]),
                "average (5-6.9)": len([g for g in grade_values if 5 <= g < 7]),
                "below_average (<5)": len([g for g in grade_values if g < 5])
            }
        }
    
    def bulk_create_subjects(self, subjects_data: List[SubjectCreate]) -> List[Subject]:
        """Create multiple subjects at once"""
        created_subjects = []
        
        for subject_data in subjects_data:
            try:
                subject = self.create_subject(subject_data)
                created_subjects.append(subject)
            except ValueError:
                # Skip duplicates
                continue
        
        return created_subjects
