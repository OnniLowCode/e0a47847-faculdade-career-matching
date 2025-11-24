"""
Pydantic schemas for Company operations
"""
from pydantic import BaseModel, EmailStr, Field, HttpUrl
from typing import Optional, List
from datetime import datetime


class CompanyBase(BaseModel):
    """Base schema for companies"""
    company_name: str = Field(min_length=2, max_length=255)
    cnpj: Optional[str] = Field(None, max_length=18)
    industry: Optional[str] = None
    size: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = Field(None, max_length=2)
    country: str = "Brasil"
    phone: Optional[str] = None
    contact_email: Optional[EmailStr] = None


class CompanyCreate(CompanyBase):
    """Schema for creating a company"""
    email: EmailStr
    password: str = Field(min_length=6)


class CompanyUpdate(BaseModel):
    """Schema for updating company profile"""
    company_name: Optional[str] = None
    industry: Optional[str] = None
    size: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    phone: Optional[str] = None
    contact_email: Optional[EmailStr] = None


class CompanyResponse(CompanyBase):
    """Schema for company response"""
    id: int
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class CompanyDetailResponse(CompanyResponse):
    """Detailed company response with jobs"""
    total_jobs: int = 0
    active_jobs: int = 0
    
    class Config:
        from_attributes = True
