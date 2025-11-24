"""
Intelligent Matching Service
Matches students with jobs based on academic performance and requirements
"""
from sqlalchemy.orm import Session
from typing import List, Dict, Tuple
from src.models.models import Student, Job, Grade, JobRequirement, Subject, MatchingLog
from src.schemas.job import MatchingResult
import json
from datetime import datetime


class MatchingService:
    """Service for matching students with job opportunities"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def calculate_match_score(
        self, 
        student_id: int, 
        job_id: int,
        save_log: bool = True
    ) -> Tuple[float, Dict]:
        """
        Calculate match score between a student and a job
        Returns: (score, details_dict)
        """
        student = self.db.query(Student).filter(Student.id == student_id).first()
        job = self.db.query(Job).filter(Job.id == job_id).first()
        
        if not student or not job:
            return 0.0, {"error": "Student or Job not found"}
        
        details = {
            "student_id": student_id,
            "job_id": job_id,
            "student_name": student.full_name,
            "job_title": job.title,
            "calculated_at": datetime.utcnow().isoformat()
        }
        
        total_score = 0.0
        max_possible_score = 0.0
        
        # 1. GPA Match (20% weight)
        gpa_weight = 20.0
        max_possible_score += gpa_weight
        
        if student.gpa >= job.minimum_gpa:
            gpa_score = gpa_weight
            # Bonus for exceeding minimum
            if job.minimum_gpa > 0:
                excess = (student.gpa - job.minimum_gpa) / (10 - job.minimum_gpa)
                gpa_score += min(excess * 5, 5)  # Up to 5 bonus points
            total_score += gpa_score
            details["gpa_match"] = True
        else:
            details["gpa_match"] = False
            details["gpa_deficit"] = job.minimum_gpa - student.gpa
        
        details["student_gpa"] = student.gpa
        details["required_gpa"] = job.minimum_gpa
        
        # 2. Semester Match (10% weight)
        semester_weight = 10.0
        max_possible_score += semester_weight
        
        if job.minimum_semester:
            if student.semester >= job.minimum_semester:
                total_score += semester_weight
                details["semester_match"] = True
            else:
                details["semester_match"] = False
                details["semester_deficit"] = job.minimum_semester - student.semester
        else:
            total_score += semester_weight
            details["semester_match"] = True
        
        details["student_semester"] = student.semester
        details["required_semester"] = job.minimum_semester
        
        # 3. Course Match (15% weight)
        course_weight = 15.0
        max_possible_score += course_weight
        
        if job.preferred_courses:
            try:
                preferred_courses = json.loads(job.preferred_courses)
            except:
                preferred_courses = [c.strip() for c in job.preferred_courses.split(",")]
            
            if student.course in preferred_courses:
                total_score += course_weight
                details["course_match"] = True
            else:
                details["course_match"] = False
        else:
            total_score += course_weight
            details["course_match"] = True
        
        details["student_course"] = student.course
        details["preferred_courses"] = job.preferred_courses
        
        # 4. Subject Requirements Match (55% weight - MOST IMPORTANT)
        subject_weight = 55.0
        max_possible_score += subject_weight
        
        job_requirements = self.db.query(JobRequirement).filter(
            JobRequirement.job_id == job_id
        ).all()
        
        if job_requirements:
            matched_subjects = []
            missing_subjects = []
            mandatory_missing = []
            
            total_requirement_weight = sum(req.weight for req in job_requirements)
            subject_score = 0.0
            
            for req in job_requirements:
                # Get student's grade for this subject
                grade = self.db.query(Grade).filter(
                    Grade.student_id == student_id,
                    Grade.subject_id == req.subject_id
                ).first()
                
                subject = self.db.query(Subject).filter(
                    Subject.id == req.subject_id
                ).first()
                
                subject_info = {
                    "subject_id": req.subject_id,
                    "subject_code": subject.code if subject else None,
                    "subject_name": subject.name if subject else None,
                    "required_grade": req.minimum_grade,
                    "weight": req.weight,
                    "is_mandatory": req.is_mandatory
                }
                
                if grade and grade.grade >= req.minimum_grade:
                    # Student meets this requirement
                    subject_info["student_grade"] = grade.grade
                    subject_info["met"] = True
                    subject_info["grade_excess"] = grade.grade - req.minimum_grade
                    matched_subjects.append(subject_info)
                    
                    # Calculate weighted score
                    grade_ratio = grade.grade / 10.0  # Normalize to 0-1
                    requirement_ratio = req.weight / total_requirement_weight
                    subject_score += (subject_weight * requirement_ratio * grade_ratio)
                    
                else:
                    # Student doesn't meet this requirement
                    subject_info["student_grade"] = grade.grade if grade else None
                    subject_info["met"] = False
                    missing_subjects.append(subject_info)
                    
                    if req.is_mandatory:
                        mandatory_missing.append(subject_info)
            
            total_score += subject_score
            
            details["matched_subjects"] = matched_subjects
            details["missing_subjects"] = missing_subjects
            details["mandatory_missing"] = mandatory_missing
            details["subject_match_percentage"] = (
                len(matched_subjects) / len(job_requirements) * 100
                if job_requirements else 100
            )
        else:
            # No specific requirements, give full score
            total_score += subject_weight
            details["matched_subjects"] = []
            details["missing_subjects"] = []
        
        # Calculate final percentage
        final_score = (total_score / max_possible_score) * 100 if max_possible_score > 0 else 0
        details["final_score"] = round(final_score, 2)
        details["raw_score"] = round(total_score, 2)
        details["max_possible_score"] = max_possible_score
        
        # Generate recommendation reason
        details["recommendation_reason"] = self._generate_recommendation(details)
        
        # Save to log if requested
        if save_log:
            log = MatchingLog(
                student_id=student_id,
                job_id=job_id,
                match_score=final_score,
                details=json.dumps(details)
            )
            self.db.add(log)
            self.db.commit()
        
        return final_score, details
    
    def find_matches_for_student(
        self, 
        student_id: int, 
        min_score: float = 50.0,
        limit: int = 10
    ) -> List[MatchingResult]:
        """
        Find best job matches for a student
        """
        from src.models.models import JobStatus
        
        # Get all open jobs
        jobs = self.db.query(Job).filter(
            Job.status == JobStatus.OPEN
        ).all()
        
        matches = []
        
        for job in jobs:
            score, details = self.calculate_match_score(student_id, job.id, save_log=False)
            
            if score >= min_score:
                company = job.company
                
                match = MatchingResult(
                    job_id=job.id,
                    job_title=job.title,
                    company_name=company.company_name if company else "N/A",
                    match_score=details.get("raw_score", 0),
                    match_percentage=score,
                    location=job.location,
                    work_type=job.work_type,
                    salary_range=job.salary_range,
                    matched_subjects=details.get("matched_subjects", []),
                    missing_subjects=details.get("missing_subjects", []),
                    gpa_match=details.get("gpa_match", False),
                    semester_match=details.get("semester_match", False),
                    course_match=details.get("course_match", False),
                    recommendation_reason=details.get("recommendation_reason", "")
                )
                matches.append(match)
        
        # Sort by match percentage (descending)
        matches.sort(key=lambda x: x.match_percentage, reverse=True)
        
        return matches[:limit]
    
    def find_candidates_for_job(
        self, 
        job_id: int, 
        min_score: float = 60.0,
        limit: int = 20
    ) -> List[Dict]:
        """
        Find best student candidates for a job
        """
        # Get all active students
        students = self.db.query(Student).join(
            Student.user
        ).filter(
            Student.user.has(is_active=True)
        ).all()
        
        candidates = []
        
        for student in students:
            score, details = self.calculate_match_score(student.id, job_id, save_log=False)
            
            if score >= min_score:
                candidates.append({
                    "student_id": student.id,
                    "student_name": student.full_name,
                    "registration_number": student.registration_number,
                    "course": student.course,
                    "semester": student.semester,
                    "gpa": student.gpa,
                    "match_score": details.get("raw_score", 0),
                    "match_percentage": score,
                    "matched_subjects": details.get("matched_subjects", []),
                    "missing_subjects": details.get("missing_subjects", []),
                    "email": student.user.email if student.user else None
                })
        
        # Sort by match percentage (descending)
        candidates.sort(key=lambda x: x["match_percentage"], reverse=True)
        
        return candidates[:limit]
    
    def _generate_recommendation(self, details: Dict) -> str:
        """Generate human-readable recommendation reason"""
        reasons = []
        
        if details.get("gpa_match"):
            reasons.append(f"GPA ({details['student_gpa']:.1f}) meets requirement")
        
        if details.get("course_match"):
            reasons.append("Course matches preferred courses")
        
        matched = len(details.get("matched_subjects", []))
        total = matched + len(details.get("missing_subjects", []))
        
        if total > 0:
            percentage = (matched / total) * 100
            reasons.append(f"{matched}/{total} required subjects met ({percentage:.0f}%)")
        
        if not reasons:
            return "General match"
        
        return "; ".join(reasons)
