"""
Matching API Routes - Intelligent job-student matching
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from src.config.database import get_db
from src.services.matching_service import MatchingService
from src.schemas.job import MatchingResult

router = APIRouter(prefix="/matching", tags=["Intelligent Matching"])


@router.get("/student/{student_id}/recommended-jobs", response_model=List[MatchingResult])
def get_recommended_jobs_for_student(
    student_id: int,
    min_score: float = Query(50.0, ge=0, le=100, description="Minimum match percentage"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results"),
    db: Session = Depends(get_db)
):
    """
    Get recommended jobs for a student based on their academic performance
    
    This endpoint uses an intelligent matching algorithm that considers:
    - Student's GPA vs job requirements
    - Specific subject grades vs job requirements
    - Course/major compatibility
    - Current semester vs minimum semester required
    
    **Matching Algorithm Weights:**
    - Subject Requirements: 55% (most important)
    - GPA Match: 20%
    - Course Match: 15%
    - Semester Match: 10%
    
    **Parameters:**
    - **student_id**: ID of the student
    - **min_score**: Minimum match percentage (0-100). Default: 50
    - **limit**: Maximum number of jobs to return. Default: 10
    
    **Returns:**
    List of jobs sorted by match percentage (highest first) with detailed matching information
    """
    from src.services.student_service import StudentService
    
    # Verify student exists
    student_service = StudentService(db)
    student = student_service.get_student_by_id(student_id)
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    # Find matches
    matching_service = MatchingService(db)
    matches = matching_service.find_matches_for_student(
        student_id=student_id,
        min_score=min_score,
        limit=limit
    )
    
    return matches


@router.get("/job/{job_id}/recommended-candidates")
def get_recommended_candidates_for_job(
    job_id: int,
    min_score: float = Query(60.0, ge=0, le=100, description="Minimum match percentage"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results"),
    db: Session = Depends(get_db)
):
    """
    Get recommended student candidates for a job posting
    
    This endpoint finds students that best match the job requirements.
    
    **Parameters:**
    - **job_id**: ID of the job
    - **min_score**: Minimum match percentage. Default: 60
    - **limit**: Maximum number of candidates. Default: 20
    
    **Returns:**
    List of students sorted by match percentage with detailed matching information
    """
    from src.services.job_service import JobService
    
    # Verify job exists
    job_service = JobService(db)
    job = job_service.get_job_by_id(job_id)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Find candidates
    matching_service = MatchingService(db)
    candidates = matching_service.find_candidates_for_job(
        job_id=job_id,
        min_score=min_score,
        limit=limit
    )
    
    return {
        "job_id": job_id,
        "job_title": job.title,
        "company_name": job.company.company_name if job.company else "",
        "total_candidates": len(candidates),
        "candidates": candidates
    }


@router.get("/calculate/{student_id}/{job_id}")
def calculate_match_score(
    student_id: int,
    job_id: int,
    db: Session = Depends(get_db)
):
    """
    Calculate detailed match score between a specific student and job
    
    Returns comprehensive matching details including:
    - Overall match score and percentage
    - GPA compatibility
    - Semester compatibility
    - Course compatibility
    - Matched subjects with grades
    - Missing/unmet requirements
    - Recommendation reasoning
    
    **Parameters:**
    - **student_id**: ID of the student
    - **job_id**: ID of the job
    
    **Returns:**
    Detailed matching breakdown with scores and recommendations
    """
    from src.services.student_service import StudentService
    from src.services.job_service import JobService
    
    # Verify both exist
    student_service = StudentService(db)
    job_service = JobService(db)
    
    student = student_service.get_student_by_id(student_id)
    job = job_service.get_job_by_id(job_id)
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Calculate match
    matching_service = MatchingService(db)
    score, details = matching_service.calculate_match_score(
        student_id=student_id,
        job_id=job_id,
        save_log=True
    )
    
    return {
        "student": {
            "id": student.id,
            "name": student.full_name,
            "course": student.course,
            "semester": student.semester,
            "gpa": student.gpa
        },
        "job": {
            "id": job.id,
            "title": job.title,
            "company": job.company.company_name if job.company else ""
        },
        "match_percentage": score,
        "details": details
    }


@router.get("/analytics/student/{student_id}")
def get_student_matching_analytics(
    student_id: int,
    db: Session = Depends(get_db)
):
    """
    Get matching analytics for a student
    
    Provides insights about:
    - Average match score across all jobs
    - Best matching job categories
    - Areas for improvement
    - Most demanded skills
    
    **Parameters:**
    - **student_id**: ID of the student
    """
    from src.services.student_service import StudentService
    from src.models.models import Job, JobStatus
    
    # Verify student exists
    student_service = StudentService(db)
    student = student_service.get_student_by_id(student_id)
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    # Get all open jobs and calculate matches
    jobs = db.query(Job).filter(Job.status == JobStatus.OPEN).all()
    
    matching_service = MatchingService(db)
    match_scores = []
    
    for job in jobs:
        score, details = matching_service.calculate_match_score(
            student_id, job.id, save_log=False
        )
        match_scores.append({
            "job_id": job.id,
            "job_title": job.title,
            "job_type": job.job_type,
            "score": score,
            "matched_subjects": len(details.get("matched_subjects", [])),
            "missing_subjects": len(details.get("missing_subjects", []))
        })
    
    # Calculate analytics
    if match_scores:
        avg_score = sum(m["score"] for m in match_scores) / len(match_scores)
        best_matches = sorted(match_scores, key=lambda x: x["score"], reverse=True)[:5]
        job_type_scores = {}
        
        for m in match_scores:
            job_type = m.get("job_type", "unknown")
            if job_type not in job_type_scores:
                job_type_scores[job_type] = []
            job_type_scores[job_type].append(m["score"])
        
        job_type_averages = {
            jt: sum(scores) / len(scores)
            for jt, scores in job_type_scores.items()
        }
    else:
        avg_score = 0
        best_matches = []
        job_type_averages = {}
    
    return {
        "student_id": student_id,
        "student_name": student.full_name,
        "total_jobs_analyzed": len(match_scores),
        "average_match_score": round(avg_score, 2),
        "best_matches": best_matches,
        "job_type_compatibility": job_type_averages,
        "academic_performance": student_service.get_academic_performance(student_id)
    }


@router.get("/analytics/job/{job_id}")
def get_job_matching_analytics(
    job_id: int,
    db: Session = Depends(get_db)
):
    """
    Get matching analytics for a job
    
    Provides insights about:
    - Number of qualified candidates
    - Average candidate match score
    - Most common gaps in requirements
    
    **Parameters:**
    - **job_id**: ID of the job
    """
    from src.services.job_service import JobService
    from src.models.models import Student
    
    # Verify job exists
    job_service = JobService(db)
    job = job_service.get_job_by_id(job_id)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Get all active students
    students = db.query(Student).join(Student.user).filter(
        Student.user.has(is_active=True)
    ).all()
    
    matching_service = MatchingService(db)
    candidate_scores = []
    
    for student in students:
        score, details = matching_service.calculate_match_score(
            student.id, job_id, save_log=False
        )
        candidate_scores.append({
            "student_id": student.id,
            "student_name": student.full_name,
            "course": student.course,
            "gpa": student.gpa,
            "score": score,
            "gpa_match": details.get("gpa_match", False),
            "course_match": details.get("course_match", False),
            "missing_subjects": details.get("missing_subjects", [])
        })
    
    # Calculate analytics
    qualified_candidates = [c for c in candidate_scores if c["score"] >= 60]
    
    if candidate_scores:
        avg_score = sum(c["score"] for c in candidate_scores) / len(candidate_scores)
        
        # Find most common missing subjects
        all_missing = []
        for c in candidate_scores:
            all_missing.extend([s["subject_name"] for s in c["missing_subjects"]])
        
        from collections import Counter
        common_gaps = Counter(all_missing).most_common(5)
    else:
        avg_score = 0
        common_gaps = []
    
    return {
        "job_id": job_id,
        "job_title": job.title,
        "company": job.company.company_name if job.company else "",
        "total_candidates_analyzed": len(candidate_scores),
        "qualified_candidates": len(qualified_candidates),
        "average_match_score": round(avg_score, 2),
        "top_candidates": sorted(qualified_candidates, key=lambda x: x["score"], reverse=True)[:10],
        "common_requirement_gaps": [
            {"subject": subj, "missing_count": count}
            for subj, count in common_gaps
        ]
    }
