"""
Pydantic schemas for Subject operations
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class SubjectBase(BaseModel):
    """Base schema for subjects"""
    code: str = Field(min_length=2, max_length=20)
    name: str = Field(min_length=3, max_length=255)
    course: str = Field(max_length=255)
    semester: Optional[int] = Field(None, ge=1, le=12)
    credits: Optional[int] = Field(None, ge=1, le=10)
    description: Optional[str] = None
    category: Optional[str] = None


class SubjectCreate(SubjectBase):
    """Schema for creating a subject"""
    pass


class SubjectUpdate(BaseModel):
    """Schema for updating a subject"""
    name: Optional[str] = None
    course: Optional[str] = None
    semester: Optional[int] = Field(None, ge=1, le=12)
    credits: Optional[int] = Field(None, ge=1, le=10)
    description: Optional[str] = None
    category: Optional[str] = None


class SubjectResponse(SubjectBase):
    """Schema for subject response"""
    id: int
    
    class Config:
        from_attributes = True


class SubjectWithStats(SubjectResponse):
    """Subject with statistics"""
    total_students: int = 0
    average_grade: Optional[float] = None
    
    class Config:
        from_attributes = True
