"""
Pydantic schemas for Job operations
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from src.models.models import JobStatus, ApplicationStatus


class SubjectRequirementBase(BaseModel):
    """Base schema for subject requirements"""
    subject_id: int
    minimum_grade: float = Field(ge=0, le=10)
    weight: float = Field(default=1.0, ge=0, le=10)
    is_mandatory: bool = False


class SubjectRequirementCreate(SubjectRequirementBase):
    """Schema for creating subject requirement"""
    pass


class SubjectRequirementResponse(SubjectRequirementBase):
    """Schema for subject requirement response"""
    id: int
    subject_code: Optional[str] = None
    subject_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class JobBase(BaseModel):
    """Base schema for jobs"""
    title: str = Field(min_length=3, max_length=255)
    description: str
    requirements: Optional[str] = None
    responsibilities: Optional[str] = None
    benefits: Optional[str] = None
    salary_range: Optional[str] = None
    location: Optional[str] = None
    work_type: Optional[str] = Field(None, example="remote")
    job_type: Optional[str] = Field(None, example="internship")
    minimum_gpa: float = Field(default=0.0, ge=0, le=10)
    minimum_semester: Optional[int] = Field(None, ge=1, le=12)
    preferred_courses: Optional[str] = None
    vacancies: int = Field(default=1, ge=1)
    deadline: Optional[datetime] = None


class JobCreate(JobBase):
    """Schema for creating a job"""
    subject_requirements: Optional[List[SubjectRequirementCreate]] = []


class JobUpdate(BaseModel):
    """Schema for updating a job"""
    title: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    responsibilities: Optional[str] = None
    benefits: Optional[str] = None
    salary_range: Optional[str] = None
    location: Optional[str] = None
    work_type: Optional[str] = None
    job_type: Optional[str] = None
    minimum_gpa: Optional[float] = Field(None, ge=0, le=10)
    minimum_semester: Optional[int] = Field(None, ge=1, le=12)
    preferred_courses: Optional[str] = None
    status: Optional[JobStatus] = None
    vacancies: Optional[int] = Field(None, ge=1)
    deadline: Optional[datetime] = None


class JobResponse(JobBase):
    """Schema for job response"""
    id: int
    company_id: int
    company_name: Optional[str] = None
    status: JobStatus
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class JobDetailResponse(JobResponse):
    """Detailed job response with requirements"""
    subject_requirements: List[SubjectRequirementResponse] = []
    total_applications: int = 0
    
    class Config:
        from_attributes = True


class JobApplicationBase(BaseModel):
    """Base schema for job applications"""
    cover_letter: Optional[str] = None


class JobApplicationCreate(JobApplicationBase):
    """Schema for creating a job application"""
    job_id: int


class JobApplicationUpdate(BaseModel):
    """Schema for updating application status"""
    status: ApplicationStatus


class JobApplicationResponse(JobApplicationBase):
    """Schema for job application response"""
    id: int
    job_id: int
    student_id: int
    status: ApplicationStatus
    match_score: Optional[float] = None
    applied_at: datetime
    job_title: Optional[str] = None
    student_name: Optional[str] = None
    company_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class MatchingResult(BaseModel):
    """Schema for matching results"""
    job_id: int
    job_title: str
    company_name: str
    match_score: float
    match_percentage: float
    location: Optional[str] = None
    work_type: Optional[str] = None
    salary_range: Optional[str] = None
    matched_subjects: List[dict] = []
    missing_subjects: List[dict] = []
    gpa_match: bool
    semester_match: bool
    course_match: bool
    recommendation_reason: str
    
    class Config:
        from_attributes = True
