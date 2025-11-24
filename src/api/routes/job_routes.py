"""
Job API Routes - Job postings and applications
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from src.config.database import get_db
from src.services.job_service import JobService
from src.models.models import JobStatus, ApplicationStatus
from src.schemas.job import (
    JobCreate, JobUpdate, JobResponse, JobDetailResponse,
    JobApplicationCreate, JobApplicationUpdate, JobApplicationResponse
)

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.post("", response_model=JobDetailResponse, status_code=status.HTTP_201_CREATED)
def create_job(
    company_id: int,
    job_data: JobCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new job posting
    
    Requires company_id in query parameter
    
    - **title**: Job title
    - **description**: Full job description
    - **minimum_gpa**: Minimum GPA required (0-10)
    - **minimum_semester**: Minimum semester required
    - **preferred_courses**: JSON array of preferred course names
    - **subject_requirements**: List of specific subject/grade requirements
    """
    service = JobService(db)
    
    try:
        job = service.create_job(company_id, job_data)
        
        # Build detailed response
        response = JobDetailResponse.model_validate(job)
        response.company_name = job.company.company_name if job.company else ""
        
        # Add subject requirements with details
        from src.schemas.job import SubjectRequirementResponse
        requirements = []
        for req in job.subject_requirements:
            req_resp = SubjectRequirementResponse.model_validate(req)
            if req.subject:
                req_resp.subject_code = req.subject.code
                req_resp.subject_name = req.subject.name
            requirements.append(req_resp)
        
        response.subject_requirements = requirements
        response.total_applications = 0
        
        return response
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("", response_model=List[JobResponse])
def list_jobs(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[JobStatus] = None,
    company_id: Optional[int] = None,
    job_type: Optional[str] = None,
    work_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List all job postings with optional filters
    
    - **status_filter**: Filter by job status (open, closed, filled)
    - **company_id**: Filter by company
    - **job_type**: Filter by job type (internship, junior, full-time, etc.)
    - **work_type**: Filter by work type (remote, hybrid, on-site)
    """
    service = JobService(db)
    jobs = service.list_jobs(
        skip=skip,
        limit=limit,
        status=status_filter,
        company_id=company_id,
        job_type=job_type,
        work_type=work_type
    )
    
    # Build responses
    responses = []
    for job in jobs:
        response = JobResponse.model_validate(job)
        response.company_name = job.company.company_name if job.company else ""
        responses.append(response)
    
    return responses


@router.get("/{job_id}", response_model=JobDetailResponse)
def get_job(
    job_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed job information including requirements
    """
    service = JobService(db)
    job = service.get_job_by_id(job_id)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Build detailed response
    response = JobDetailResponse.model_validate(job)
    response.company_name = job.company.company_name if job.company else ""
    
    # Add subject requirements with details
    from src.schemas.job import SubjectRequirementResponse
    requirements = []
    for req in job.subject_requirements:
        req_resp = SubjectRequirementResponse.model_validate(req)
        if req.subject:
            req_resp.subject_code = req.subject.code
            req_resp.subject_name = req.subject.name
        requirements.append(req_resp)
    
    response.subject_requirements = requirements
    response.total_applications = len(job.applications)
    
    return response


@router.put("/{job_id}", response_model=JobResponse)
def update_job(
    job_id: int,
    job_data: JobUpdate,
    db: Session = Depends(get_db)
):
    """
    Update job posting
    """
    service = JobService(db)
    job = service.update_job(job_id, job_data)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    response = JobResponse.model_validate(job)
    response.company_name = job.company.company_name if job.company else ""
    
    return response


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(
    job_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a job posting
    """
    service = JobService(db)
    success = service.delete_job(job_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    return None


@router.post("/applications", response_model=JobApplicationResponse, status_code=status.HTTP_201_CREATED)
def apply_to_job(
    student_id: int,
    application_data: JobApplicationCreate,
    db: Session = Depends(get_db)
):
    """
    Student applies to a job
    
    Requires student_id in query parameter
    """
    service = JobService(db)
    
    # Calculate match score before applying
    from src.services.matching_service import MatchingService
    matching_service = MatchingService(db)
    match_score, _ = matching_service.calculate_match_score(
        student_id, 
        application_data.job_id,
        save_log=True
    )
    
    try:
        application = service.apply_to_job(student_id, application_data, match_score)
        
        # Build response
        response = JobApplicationResponse.model_validate(application)
        response.job_title = application.job.title if application.job else ""
        response.student_name = application.student.full_name if application.student else ""
        response.company_name = application.job.company.company_name if application.job and application.job.company else ""
        
        return response
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{job_id}/applications", response_model=List[JobApplicationResponse])
def get_job_applications(
    job_id: int,
    status_filter: Optional[ApplicationStatus] = None,
    db: Session = Depends(get_db)
):
    """
    Get all applications for a job
    
    - **status_filter**: Filter by application status (pending, approved, rejected, interview)
    """
    service = JobService(db)
    applications = service.get_job_applications(job_id, status_filter)
    
    # Build responses
    responses = []
    for app in applications:
        response = JobApplicationResponse.model_validate(app)
        response.job_title = app.job.title if app.job else ""
        response.student_name = app.student.full_name if app.student else ""
        response.company_name = app.job.company.company_name if app.job and app.job.company else ""
        responses.append(response)
    
    return responses


@router.get("/applications/student/{student_id}", response_model=List[JobApplicationResponse])
def get_student_applications(
    student_id: int,
    status_filter: Optional[ApplicationStatus] = None,
    db: Session = Depends(get_db)
):
    """
    Get all applications from a student
    """
    service = JobService(db)
    applications = service.get_student_applications(student_id, status_filter)
    
    # Build responses
    responses = []
    for app in applications:
        response = JobApplicationResponse.model_validate(app)
        response.job_title = app.job.title if app.job else ""
        response.student_name = app.student.full_name if app.student else ""
        response.company_name = app.job.company.company_name if app.job and app.job.company else ""
        responses.append(response)
    
    return responses


@router.patch("/applications/{application_id}", response_model=JobApplicationResponse)
def update_application_status(
    application_id: int,
    status_update: JobApplicationUpdate,
    db: Session = Depends(get_db)
):
    """
    Update application status (for companies)
    """
    service = JobService(db)
    application = service.update_application_status(application_id, status_update.status)
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    response = JobApplicationResponse.model_validate(application)
    response.job_title = application.job.title if application.job else ""
    response.student_name = application.student.full_name if application.student else ""
    response.company_name = application.job.company.company_name if application.job and application.job.company else ""
    
    return response
