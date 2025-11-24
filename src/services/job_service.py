"""
Job Service - Business logic for job and company operations
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from src.models.models import Job, Company, User, UserRole, JobRequirement, JobApplication, ApplicationStatus, JobStatus
from src.schemas.company import CompanyCreate, CompanyUpdate
from src.schemas.job import JobCreate, JobUpdate, JobApplicationCreate
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class CompanyService:
    """Service for company operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_company(self, company_data: CompanyCreate) -> Company:
        """Create a new company with user account"""
        # Check if email already exists
        existing_user = self.db.query(User).filter(
            User.email == company_data.email
        ).first()
        
        if existing_user:
            raise ValueError("Email already registered")
        
        # Check CNPJ if provided
        if company_data.cnpj:
            existing_company = self.db.query(Company).filter(
                Company.cnpj == company_data.cnpj
            ).first()
            
            if existing_company:
                raise ValueError("CNPJ already registered")
        
        # Create user
        hashed_password = pwd_context.hash(company_data.password)
        user = User(
            email=company_data.email,
            hashed_password=hashed_password,
            role=UserRole.COMPANY,
            is_active=True
        )
        self.db.add(user)
        self.db.flush()
        
        # Create company profile
        company = Company(
            user_id=user.id,
            company_name=company_data.company_name,
            cnpj=company_data.cnpj,
            industry=company_data.industry,
            size=company_data.size,
            website=company_data.website,
            description=company_data.description,
            logo_url=company_data.logo_url,
            address=company_data.address,
            city=company_data.city,
            state=company_data.state,
            country=company_data.country,
            phone=company_data.phone,
            contact_email=company_data.contact_email
        )
        self.db.add(company)
        self.db.commit()
        self.db.refresh(company)
        
        return company
    
    def get_company_by_id(self, company_id: int) -> Optional[Company]:
        """Get company by ID"""
        return self.db.query(Company).filter(Company.id == company_id).first()
    
    def get_company_by_user_id(self, user_id: int) -> Optional[Company]:
        """Get company by user ID"""
        return self.db.query(Company).filter(Company.user_id == user_id).first()
    
    def list_companies(self, skip: int = 0, limit: int = 100) -> List[Company]:
        """List all companies"""
        return self.db.query(Company).offset(skip).limit(limit).all()
    
    def update_company(
        self, 
        company_id: int, 
        company_data: CompanyUpdate
    ) -> Optional[Company]:
        """Update company profile"""
        company = self.get_company_by_id(company_id)
        
        if not company:
            return None
        
        update_data = company_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(company, field, value)
        
        self.db.commit()
        self.db.refresh(company)
        
        return company


class JobService:
    """Service for job posting operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_job(self, company_id: int, job_data: JobCreate) -> Job:
        """Create a new job posting"""
        # Verify company exists
        company = self.db.query(Company).filter(Company.id == company_id).first()
        
        if not company:
            raise ValueError("Company not found")
        
        # Create job
        job = Job(
            company_id=company_id,
            title=job_data.title,
            description=job_data.description,
            requirements=job_data.requirements,
            responsibilities=job_data.responsibilities,
            benefits=job_data.benefits,
            salary_range=job_data.salary_range,
            location=job_data.location,
            work_type=job_data.work_type,
            job_type=job_data.job_type,
            minimum_gpa=job_data.minimum_gpa,
            minimum_semester=job_data.minimum_semester,
            preferred_courses=job_data.preferred_courses,
            vacancies=job_data.vacancies,
            deadline=job_data.deadline,
            status=JobStatus.OPEN
        )
        self.db.add(job)
        self.db.flush()
        
        # Add subject requirements
        if job_data.subject_requirements:
            for req_data in job_data.subject_requirements:
                requirement = JobRequirement(
                    job_id=job.id,
                    subject_id=req_data.subject_id,
                    minimum_grade=req_data.minimum_grade,
                    weight=req_data.weight,
                    is_mandatory=req_data.is_mandatory
                )
                self.db.add(requirement)
        
        self.db.commit()
        self.db.refresh(job)
        
        return job
    
    def get_job_by_id(self, job_id: int) -> Optional[Job]:
        """Get job by ID"""
        return self.db.query(Job).filter(Job.id == job_id).first()
    
    def list_jobs(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[JobStatus] = None,
        company_id: Optional[int] = None,
        job_type: Optional[str] = None,
        work_type: Optional[str] = None
    ) -> List[Job]:
        """List jobs with filters"""
        query = self.db.query(Job)
        
        if status:
            query = query.filter(Job.status == status)
        
        if company_id:
            query = query.filter(Job.company_id == company_id)
        
        if job_type:
            query = query.filter(Job.job_type == job_type)
        
        if work_type:
            query = query.filter(Job.work_type == work_type)
        
        return query.order_by(Job.created_at.desc()).offset(skip).limit(limit).all()
    
    def update_job(self, job_id: int, job_data: JobUpdate) -> Optional[Job]:
        """Update job posting"""
        job = self.get_job_by_id(job_id)
        
        if not job:
            return None
        
        update_data = job_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(job, field, value)
        
        self.db.commit()
        self.db.refresh(job)
        
        return job
    
    def delete_job(self, job_id: int) -> bool:
        """Delete a job posting"""
        job = self.get_job_by_id(job_id)
        
        if not job:
            return False
        
        self.db.delete(job)
        self.db.commit()
        
        return True
    
    def apply_to_job(
        self, 
        student_id: int, 
        application_data: JobApplicationCreate,
        match_score: Optional[float] = None
    ) -> JobApplication:
        """Student applies to a job"""
        # Check if already applied
        existing = self.db.query(JobApplication).filter(
            JobApplication.job_id == application_data.job_id,
            JobApplication.student_id == student_id
        ).first()
        
        if existing:
            raise ValueError("Already applied to this job")
        
        # Verify job exists and is open
        job = self.get_job_by_id(application_data.job_id)
        
        if not job:
            raise ValueError("Job not found")
        
        if job.status != JobStatus.OPEN:
            raise ValueError("Job is not accepting applications")
        
        # Create application
        application = JobApplication(
            job_id=application_data.job_id,
            student_id=student_id,
            cover_letter=application_data.cover_letter,
            match_score=match_score,
            status=ApplicationStatus.PENDING
        )
        self.db.add(application)
        self.db.commit()
        self.db.refresh(application)
        
        return application
    
    def get_job_applications(
        self, 
        job_id: int,
        status: Optional[ApplicationStatus] = None
    ) -> List[JobApplication]:
        """Get applications for a job"""
        query = self.db.query(JobApplication).filter(
            JobApplication.job_id == job_id
        )
        
        if status:
            query = query.filter(JobApplication.status == status)
        
        return query.order_by(JobApplication.match_score.desc()).all()
    
    def get_student_applications(
        self, 
        student_id: int,
        status: Optional[ApplicationStatus] = None
    ) -> List[JobApplication]:
        """Get student's applications"""
        query = self.db.query(JobApplication).filter(
            JobApplication.student_id == student_id
        )
        
        if status:
            query = query.filter(JobApplication.status == status)
        
        return query.order_by(JobApplication.applied_at.desc()).all()
    
    def update_application_status(
        self, 
        application_id: int, 
        new_status: ApplicationStatus
    ) -> Optional[JobApplication]:
        """Update application status"""
        application = self.db.query(JobApplication).filter(
            JobApplication.id == application_id
        ).first()
        
        if not application:
            return None
        
        application.status = new_status
        self.db.commit()
        self.db.refresh(application)
        
        return application
