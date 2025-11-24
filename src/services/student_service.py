"""
Student Service - Business logic for student operations
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from src.models.models import Student, User, UserRole, Grade, Subject
from src.schemas.student import StudentCreate, StudentUpdate, GradeCreate
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class StudentService:
    """Service for student operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_student(self, student_data: StudentCreate) -> Student:
        """Create a new student with user account"""
        # Check if email already exists
        existing_user = self.db.query(User).filter(
            User.email == student_data.email
        ).first()
        
        if existing_user:
            raise ValueError("Email already registered")
        
        # Check if registration number exists
        existing_student = self.db.query(Student).filter(
            Student.registration_number == student_data.registration_number
        ).first()
        
        if existing_student:
            raise ValueError("Registration number already exists")
        
        # Create user
        hashed_password = pwd_context.hash(student_data.password)
        user = User(
            email=student_data.email,
            hashed_password=hashed_password,
            role=UserRole.STUDENT,
            is_active=True
        )
        self.db.add(user)
        self.db.flush()
        
        # Create student profile
        student = Student(
            user_id=user.id,
            full_name=student_data.full_name,
            registration_number=student_data.registration_number,
            course=student_data.course,
            semester=student_data.semester,
            phone=student_data.phone,
            linkedin_url=student_data.linkedin_url,
            github_url=student_data.github_url,
            portfolio_url=student_data.portfolio_url,
            bio=student_data.bio,
            skills=student_data.skills
        )
        self.db.add(student)
        self.db.commit()
        self.db.refresh(student)
        
        return student
    
    def get_student_by_id(self, student_id: int) -> Optional[Student]:
        """Get student by ID"""
        return self.db.query(Student).filter(Student.id == student_id).first()
    
    def get_student_by_registration(self, registration_number: str) -> Optional[Student]:
        """Get student by registration number"""
        return self.db.query(Student).filter(
            Student.registration_number == registration_number
        ).first()
    
    def get_student_by_user_id(self, user_id: int) -> Optional[Student]:
        """Get student by user ID"""
        return self.db.query(Student).filter(Student.user_id == user_id).first()
    
    def list_students(
        self, 
        skip: int = 0, 
        limit: int = 100,
        course: Optional[str] = None,
        semester: Optional[int] = None
    ) -> List[Student]:
        """List students with optional filters"""
        query = self.db.query(Student)
        
        if course:
            query = query.filter(Student.course == course)
        
        if semester:
            query = query.filter(Student.semester == semester)
        
        return query.offset(skip).limit(limit).all()
    
    def update_student(
        self, 
        student_id: int, 
        student_data: StudentUpdate
    ) -> Optional[Student]:
        """Update student profile"""
        student = self.get_student_by_id(student_id)
        
        if not student:
            return None
        
        update_data = student_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(student, field, value)
        
        self.db.commit()
        self.db.refresh(student)
        
        # Recalculate GPA
        self.update_gpa(student_id)
        
        return student
    
    def add_grade(self, student_id: int, grade_data: GradeCreate) -> Grade:
        """Add or update a grade for a student"""
        # Check if grade already exists
        existing_grade = self.db.query(Grade).filter(
            Grade.student_id == student_id,
            Grade.subject_id == grade_data.subject_id,
            Grade.semester_year == grade_data.semester_year
        ).first()
        
        if existing_grade:
            # Update existing grade
            existing_grade.grade = grade_data.grade
            self.db.commit()
            self.db.refresh(existing_grade)
            grade = existing_grade
        else:
            # Create new grade
            grade = Grade(
                student_id=student_id,
                subject_id=grade_data.subject_id,
                grade=grade_data.grade,
                semester_year=grade_data.semester_year
            )
            self.db.add(grade)
            self.db.commit()
            self.db.refresh(grade)
        
        # Update student GPA
        self.update_gpa(student_id)
        
        return grade
    
    def get_student_grades(self, student_id: int) -> List[Grade]:
        """Get all grades for a student"""
        return self.db.query(Grade).filter(
            Grade.student_id == student_id
        ).all()
    
    def update_gpa(self, student_id: int) -> float:
        """Recalculate and update student GPA"""
        grades = self.db.query(Grade).filter(
            Grade.student_id == student_id
        ).all()
        
        if not grades:
            gpa = 0.0
        else:
            total_grade = sum(g.grade for g in grades)
            gpa = total_grade / len(grades)
        
        student = self.get_student_by_id(student_id)
        if student:
            student.gpa = round(gpa, 2)
            self.db.commit()
        
        return gpa
    
    def delete_student(self, student_id: int) -> bool:
        """Delete a student"""
        student = self.get_student_by_id(student_id)
        
        if not student:
            return False
        
        # Delete associated user
        if student.user:
            self.db.delete(student.user)
        
        self.db.delete(student)
        self.db.commit()
        
        return True
    
    def get_academic_performance(self, student_id: int) -> dict:
        """Get detailed academic performance metrics"""
        student = self.get_student_by_id(student_id)
        
        if not student:
            return {}
        
        grades = self.get_student_grades(student_id)
        
        # Group grades by category
        category_performance = {}
        
        for grade in grades:
            subject = self.db.query(Subject).filter(
                Subject.id == grade.subject_id
            ).first()
            
            if subject and subject.category:
                if subject.category not in category_performance:
                    category_performance[subject.category] = []
                category_performance[subject.category].append(grade.grade)
        
        # Calculate average per category
        category_averages = {
            cat: round(sum(grades_list) / len(grades_list), 2)
            for cat, grades_list in category_performance.items()
        }
        
        return {
            "student_id": student_id,
            "gpa": student.gpa,
            "total_subjects": len(grades),
            "category_averages": category_averages,
            "best_category": max(category_averages.items(), key=lambda x: x[1])[0] if category_averages else None,
            "grades_distribution": {
                "excellent (9-10)": len([g for g in grades if g.grade >= 9]),
                "good (7-8.9)": len([g for g in grades if 7 <= g.grade < 9]),
                "average (5-6.9)": len([g for g in grades if 5 <= g.grade < 7]),
                "below_average (<5)": len([g for g in grades if g.grade < 5])
            }
        }
