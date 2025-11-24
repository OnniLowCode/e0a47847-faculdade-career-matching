"""
Database models for the Faculty Career Matching System
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.config.database import Base
import enum


class UserRole(str, enum.Enum):
    """User roles in the system"""
    STUDENT = "student"
    COMPANY = "company"
    ADMIN = "admin"
    COORDINATOR = "coordinator"


class JobStatus(str, enum.Enum):
    """Job posting status"""
    OPEN = "open"
    CLOSED = "closed"
    FILLED = "filled"


class ApplicationStatus(str, enum.Enum):
    """Application status"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    INTERVIEW = "interview"


class User(Base):
    """User model for authentication"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    student_profile = relationship("Student", back_populates="user", uselist=False)
    company_profile = relationship("Company", back_populates="user", uselist=False)


class Student(Base):
    """Student profile with academic information"""
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    full_name = Column(String(255), nullable=False)
    registration_number = Column(String(50), unique=True, nullable=False, index=True)
    course = Column(String(255), nullable=False)
    semester = Column(Integer, nullable=False)
    gpa = Column(Float, default=0.0)  # Grade Point Average
    phone = Column(String(20))
    linkedin_url = Column(String(255))
    github_url = Column(String(255))
    portfolio_url = Column(String(255))
    bio = Column(Text)
    skills = Column(Text)  # JSON string of skills
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="student_profile")
    grades = relationship("Grade", back_populates="student", cascade="all, delete-orphan")
    applications = relationship("JobApplication", back_populates="student", cascade="all, delete-orphan")


class Subject(Base):
    """Academic subjects/disciplines"""
    __tablename__ = "subjects"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    course = Column(String(255), nullable=False)
    semester = Column(Integer)
    credits = Column(Integer)
    description = Column(Text)
    category = Column(String(100))  # e.g., "programming", "mathematics", "business"
    
    # Relationships
    grades = relationship("Grade", back_populates="subject")
    job_requirements = relationship("JobRequirement", back_populates="subject")


class Grade(Base):
    """Student grades for subjects"""
    __tablename__ = "grades"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    grade = Column(Float, nullable=False)  # 0-10 scale
    semester_year = Column(String(20))  # e.g., "2024.1"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    student = relationship("Student", back_populates="grades")
    subject = relationship("Subject", back_populates="grades")


class Company(Base):
    """Company profile"""
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    company_name = Column(String(255), nullable=False)
    cnpj = Column(String(18), unique=True)  # Brazilian company ID
    industry = Column(String(100))
    size = Column(String(50))  # e.g., "1-10", "11-50", "51-200", etc.
    website = Column(String(255))
    description = Column(Text)
    logo_url = Column(String(255))
    address = Column(String(255))
    city = Column(String(100))
    state = Column(String(2))
    country = Column(String(100), default="Brasil")
    phone = Column(String(20))
    contact_email = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="company_profile")
    jobs = relationship("Job", back_populates="company", cascade="all, delete-orphan")


class Job(Base):
    """Job postings from companies"""
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    requirements = Column(Text)  # General text requirements
    responsibilities = Column(Text)
    benefits = Column(Text)
    salary_range = Column(String(100))
    location = Column(String(255))
    work_type = Column(String(50))  # remote, hybrid, on-site
    job_type = Column(String(50))  # internship, junior, full-time, part-time
    minimum_gpa = Column(Float, default=0.0)
    minimum_semester = Column(Integer)
    preferred_courses = Column(Text)  # JSON string of courses
    status = Column(SQLEnum(JobStatus), default=JobStatus.OPEN)
    vacancies = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deadline = Column(DateTime(timezone=True))
    
    # Relationships
    company = relationship("Company", back_populates="jobs")
    subject_requirements = relationship("JobRequirement", back_populates="job", cascade="all, delete-orphan")
    applications = relationship("JobApplication", back_populates="job", cascade="all, delete-orphan")


class JobRequirement(Base):
    """Specific subject/grade requirements for jobs"""
    __tablename__ = "job_requirements"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    minimum_grade = Column(Float, nullable=False)  # Minimum grade required
    weight = Column(Float, default=1.0)  # Weight for matching algorithm
    is_mandatory = Column(Boolean, default=False)  # Must have this subject
    
    # Relationships
    job = relationship("Job", back_populates="subject_requirements")
    subject = relationship("Subject", back_populates="job_requirements")


class JobApplication(Base):
    """Student applications to jobs"""
    __tablename__ = "job_applications"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    status = Column(SQLEnum(ApplicationStatus), default=ApplicationStatus.PENDING)
    match_score = Column(Float)  # Calculated matching score
    cover_letter = Column(Text)
    applied_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    job = relationship("Job", back_populates="applications")
    student = relationship("Student", back_populates="applications")


class MatchingLog(Base):
    """Log of matching calculations for analytics"""
    __tablename__ = "matching_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    job_id = Column(Integer, ForeignKey("jobs.id"))
    match_score = Column(Float)
    details = Column(Text)  # JSON with matching details
    created_at = Column(DateTime(timezone=True), server_default=func.now())
