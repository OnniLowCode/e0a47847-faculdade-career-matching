"""
Pydantic schemas for Student operations
"""
from pydantic import BaseModel, EmailStr, Field, HttpUrl
from typing import Optional, List
from datetime import datetime


class GradeBase(BaseModel):
    """Base schema for grades"""
    subject_id: int
    grade: float = Field(ge=0, le=10, description="Grade from 0 to 10")
    semester_year: str = Field(example="2024.1")


class GradeCreate(GradeBase):
    """Schema for creating a grade"""
    pass


class GradeResponse(GradeBase):
    """Schema for grade response"""
    id: int
    student_id: int
    subject_name: Optional[str] = None
    subject_code: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class StudentBase(BaseModel):
    """Base schema for students"""
    full_name: str = Field(min_length=3, max_length=255)
    course: str = Field(max_length=255)
    semester: int = Field(ge=1, le=12)
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    bio: Optional[str] = None
    skills: Optional[str] = None  # Comma-separated or JSON


class StudentCreate(StudentBase):
    """Schema for creating a student"""
    email: EmailStr
    password: str = Field(min_length=6)
    registration_number: str = Field(min_length=3, max_length=50)


class StudentUpdate(BaseModel):
    """Schema for updating student profile"""
    full_name: Optional[str] = None
    course: Optional[str] = None
    semester: Optional[int] = Field(None, ge=1, le=12)
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    bio: Optional[str] = None
    skills: Optional[str] = None


class StudentResponse(StudentBase):
    """Schema for student response"""
    id: int
    registration_number: str
    gpa: float
    email: str
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class StudentDetailResponse(StudentResponse):
    """Detailed student response with grades"""
    grades: List[GradeResponse] = []
    total_credits: Optional[int] = 0
    
    class Config:
        from_attributes = True


class StudentAcademicProfile(BaseModel):
    """Academic profile for matching"""
    student_id: int
    full_name: str
    course: str
    semester: int
    gpa: float
    grades_by_subject: dict  # {subject_code: grade}
    skills: List[str] = []
    
    class Config:
        from_attributes = True
