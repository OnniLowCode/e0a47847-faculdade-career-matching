"""
Seed Data - Populate database with example data
"""
from sqlalchemy.orm import Session
from src.config.database import SessionLocal
from src.services.student_service import StudentService
from src.services.job_service import CompanyService, JobService
from src.services.subject_service import SubjectService
from src.schemas.student import StudentCreate, GradeCreate
from src.schemas.company import CompanyCreate
from src.schemas.job import JobCreate, SubjectRequirementCreate
from src.schemas.subject import SubjectCreate


def seed_subjects(db: Session):
    """Create example subjects for Computer Science course"""
    print("📚 Creating subjects...")
    
    service = SubjectService(db)
    
    subjects = [
        # Programming subjects
        SubjectCreate(
            code="CS101",
            name="Introdução à Programação",
            course="Ciência da Computação",
            semester=1,
            credits=4,
            category="programming",
            description="Fundamentos de programação"
        ),
        SubjectCreate(
            code="CS102",
            name="Estruturas de Dados",
            course="Ciência da Computação",
            semester=2,
            credits=4,
            category="programming",
            description="Estruturas de dados e algoritmos"
        ),
        SubjectCreate(
            code="CS201",
            name="Programação Orientada a Objetos",
            course="Ciência da Computação",
            semester=3,
            credits=4,
            category="programming",
            description="POO com Java/Python"
        ),
        SubjectCreate(
            code="CS202",
            name="Banco de Dados",
            course="Ciência da Computação",
            semester=4,
            credits=4,
            category="database",
            description="SQL, NoSQL e modelagem de dados"
        ),
        SubjectCreate(
            code="CS301",
            name="Desenvolvimento Web",
            course="Ciência da Computação",
            semester=5,
            credits=4,
            category="web",
            description="HTML, CSS, JavaScript, frameworks"
        ),
        SubjectCreate(
            code="CS302",
            name="Engenharia de Software",
            course="Ciência da Computação",
            semester=5,
            credits=4,
            category="software_engineering",
            description="Metodologias ágeis, padrões de projeto"
        ),
        # Mathematics subjects
        SubjectCreate(
            code="MAT101",
            name="Cálculo I",
            course="Ciência da Computação",
            semester=1,
            credits=4,
            category="mathematics",
            description="Limites, derivadas e integrais"
        ),
        SubjectCreate(
            code="MAT201",
            name="Estatística",
            course="Ciência da Computação",
            semester=3,
            credits=4,
            category="mathematics",
            description="Probabilidade e estatística"
        ),
        # Business/Management
        SubjectCreate(
            code="ADM101",
            name="Gestão de Projetos",
            course="Ciência da Computação",
            semester=6,
            credits=3,
            category="management",
            description="Gerenciamento de projetos de TI"
        ),
        SubjectCreate(
            code="ADM201",
            name="Empreendedorismo",
            course="Ciência da Computação",
            semester=7,
            credits=2,
            category="business",
            description="Criação e gestão de startups"
        ),
    ]
    
    created = service.bulk_create_subjects(subjects)
    print(f"✅ Created {len(created)} subjects")
    
    return created


def seed_students(db: Session):
    """Create example students with grades"""
    print("👨‍🎓 Creating students...")
    
    service = StudentService(db)
    subject_service = SubjectService(db)
    
    students_data = [
        {
            "data": StudentCreate(
                email="joao.silva@university.edu",
                password="senha123",
                registration_number="2021001",
                full_name="João Silva",
                course="Ciência da Computação",
                semester=5,
                phone="+5511999999001",
                linkedin_url="https://linkedin.com/in/joaosilva",
                github_url="https://github.com/joaosilva",
                bio="Estudante de CC apaixonado por desenvolvimento web",
                skills="Python, JavaScript, React, Node.js"
            ),
            "grades": {
                "CS101": 9.5,
                "CS102": 8.7,
                "CS201": 9.0,
                "CS202": 8.5,
                "CS301": 9.2,
                "MAT101": 7.5,
                "MAT201": 8.0
            }
        },
        {
            "data": StudentCreate(
                email="maria.santos@university.edu",
                password="senha123",
                registration_number="2021002",
                full_name="Maria Santos",
                course="Ciência da Computação",
                semester=6,
                phone="+5511999999002",
                linkedin_url="https://linkedin.com/in/mariasantos",
                github_url="https://github.com/mariasantos",
                bio="Desenvolvedora full-stack e entusiasta de IA",
                skills="Java, Python, SQL, Machine Learning"
            ),
            "grades": {
                "CS101": 10.0,
                "CS102": 9.5,
                "CS201": 9.8,
                "CS202": 9.0,
                "CS301": 8.5,
                "CS302": 9.3,
                "MAT101": 8.5,
                "MAT201": 9.0
            }
        },
        {
            "data": StudentCreate(
                email="pedro.oliveira@university.edu",
                password="senha123",
                registration_number="2022001",
                full_name="Pedro Oliveira",
                course="Ciência da Computação",
                semester=3,
                phone="+5511999999003",
                github_url="https://github.com/pedrooliveira",
                bio="Iniciante em programação, focado em backend",
                skills="Python, Django, PostgreSQL"
            ),
            "grades": {
                "CS101": 7.0,
                "CS102": 7.5,
                "CS201": 8.0,
                "MAT101": 6.5
            }
        }
    ]
    
    created_students = []
    
    for student_info in students_data:
        try:
            student = service.create_student(student_info["data"])
            created_students.append(student)
            
            # Add grades
            for subject_code, grade_value in student_info["grades"].items():
                subject = subject_service.get_subject_by_code(subject_code)
                if subject:
                    grade_data = GradeCreate(
                        subject_id=subject.id,
                        grade=grade_value,
                        semester_year="2024.1"
                    )
                    service.add_grade(student.id, grade_data)
            
            print(f"✅ Created student: {student.full_name}")
        except Exception as e:
            print(f"⚠️  Error creating student: {e}")
    
    return created_students


def seed_companies(db: Session):
    """Create example companies"""
    print("🏢 Creating companies...")
    
    service = CompanyService(db)
    
    companies_data = [
        CompanyCreate(
            email="rh@techsolutions.com",
            password="senha123",
            company_name="Tech Solutions Brasil",
            cnpj="12.345.678/0001-90",
            industry="Tecnologia da Informação",
            size="51-200",
            website="https://techsolutions.com.br",
            description="Empresa de desenvolvimento de software e consultoria em TI",
            city="São Paulo",
            state="SP",
            phone="+5511988880001",
            contact_email="contato@techsolutions.com"
        ),
        CompanyCreate(
            email="rh@startupai.com",
            password="senha123",
            company_name="StartupAI",
            cnpj="98.765.432/0001-10",
            industry="Inteligência Artificial",
            size="11-50",
            website="https://startupai.com.br",
            description="Startup focada em soluções de IA e Machine Learning",
            city="São Paulo",
            state="SP",
            phone="+5511988880002",
            contact_email="jobs@startupai.com"
        ),
        CompanyCreate(
            email="rh@webagency.com",
            password="senha123",
            company_name="Web Agency Digital",
            cnpj="11.222.333/0001-44",
            industry="Marketing Digital",
            size="11-50",
            website="https://webagency.com.br",
            description="Agência de marketing digital e desenvolvimento web",
            city="Rio de Janeiro",
            state="RJ",
            phone="+5521988880003",
            contact_email="vagas@webagency.com"
        )
    ]
    
    created_companies = []
    
    for company_data in companies_data:
        try:
            company = service.create_company(company_data)
            created_companies.append(company)
            print(f"✅ Created company: {company.company_name}")
        except Exception as e:
            print(f"⚠️  Error creating company: {e}")
    
    return created_companies


def seed_jobs(db: Session, companies: list):
    """Create example job postings"""
    print("💼 Creating job postings...")
    
    job_service = JobService(db)
    subject_service = SubjectService(db)
    
    # Tech Solutions jobs
    tech_company = companies[0]
    
    # Job 1: Junior Backend Developer
    cs202_db = subject_service.get_subject_by_code("CS202")
    cs201_oop = subject_service.get_subject_by_code("CS201")
    cs102_ds = subject_service.get_subject_by_code("CS102")
    
    job1 = JobCreate(
        title="Desenvolvedor Backend Júnior",
        description="Buscamos desenvolvedor backend júnior para trabalhar com Python/Django em projetos de clientes",
        requirements="Conhecimento em programação orientada a objetos, banco de dados e estruturas de dados",
        responsibilities="Desenvolver APIs REST, trabalhar com bancos de dados, colaborar com equipe",
        benefits="Vale refeição, plano de saúde, home office flexível",
        salary_range="R$ 3.500 - R$ 5.000",
        location="São Paulo, SP (Híbrido)",
        work_type="hybrid",
        job_type="junior",
        minimum_gpa=7.0,
        minimum_semester=4,
        preferred_courses='["Ciência da Computação", "Engenharia de Software"]',
        vacancies=2,
        subject_requirements=[
            SubjectRequirementCreate(
                subject_id=cs202_db.id,
                minimum_grade=7.5,
                weight=2.0,
                is_mandatory=True
            ),
            SubjectRequirementCreate(
                subject_id=cs201_oop.id,
                minimum_grade=7.0,
                weight=1.5,
                is_mandatory=True
            ),
            SubjectRequirementCreate(
                subject_id=cs102_ds.id,
                minimum_grade=7.0,
                weight=1.0,
                is_mandatory=False
            )
        ]
    )
    
    try:
        job_service.create_job(tech_company.id, job1)
        print("✅ Created job: Desenvolvedor Backend Júnior")
    except Exception as e:
        print(f"⚠️  Error: {e}")
    
    # Job 2: Web Developer Intern
    cs301_web = subject_service.get_subject_by_code("CS301")
    cs101_prog = subject_service.get_subject_by_code("CS101")
    
    startup_company = companies[1]
    
    job2 = JobCreate(
        title="Estágio em Desenvolvimento Web",
        description="Oportunidade de estágio em desenvolvimento web com foco em React e Node.js",
        requirements="Conhecimentos básicos em desenvolvimento web e programação",
        responsibilities="Desenvolver interfaces web, integrar com APIs, testes",
        benefits="Bolsa auxílio, vale transporte, mentoria técnica",
        salary_range="R$ 1.500 - R$ 2.000",
        location="São Paulo, SP (Remoto)",
        work_type="remote",
        job_type="internship",
        minimum_gpa=6.0,
        minimum_semester=3,
        preferred_courses='["Ciência da Computação", "Sistemas de Informação"]',
        vacancies=3,
        subject_requirements=[
            SubjectRequirementCreate(
                subject_id=cs301_web.id,
                minimum_grade=7.0,
                weight=2.0,
                is_mandatory=True
            ),
            SubjectRequirementCreate(
                subject_id=cs101_prog.id,
                minimum_grade=6.0,
                weight=1.0,
                is_mandatory=True
            )
        ]
    )
    
    try:
        job_service.create_job(startup_company.id, job2)
        print("✅ Created job: Estágio em Desenvolvimento Web")
    except Exception as e:
        print(f"⚠️  Error: {e}")
    
    # Job 3: Full Stack Developer
    cs302_eng = subject_service.get_subject_by_code("CS302")
    
    agency_company = companies[2]
    
    job3 = JobCreate(
        title="Desenvolvedor Full Stack",
        description="Desenvolvedor full stack para projetos de clientes variados",
        requirements="Experiência com desenvolvimento web, banco de dados e engenharia de software",
        responsibilities="Desenvolver aplicações completas, front e backend",
        benefits="CLT, plano de saúde, VR, VA, participação nos lucros",
        salary_range="R$ 5.000 - R$ 8.000",
        location="Rio de Janeiro, RJ",
        work_type="on-site",
        job_type="full-time",
        minimum_gpa=7.5,
        minimum_semester=5,
        preferred_courses='["Ciência da Computação"]',
        vacancies=1,
        subject_requirements=[
            SubjectRequirementCreate(
                subject_id=cs301_web.id,
                minimum_grade=8.0,
                weight=2.0,
                is_mandatory=True
            ),
            SubjectRequirementCreate(
                subject_id=cs202_db.id,
                minimum_grade=7.5,
                weight=1.5,
                is_mandatory=True
            ),
            SubjectRequirementCreate(
                subject_id=cs302_eng.id,
                minimum_grade=7.0,
                weight=1.0,
                is_mandatory=False
            )
        ]
    )
    
    try:
        job_service.create_job(agency_company.id, job3)
        print("✅ Created job: Desenvolvedor Full Stack")
    except Exception as e:
        print(f"⚠️  Error: {e}")


def seed_all():
    """Seed all example data"""
    print("\n🌱 Starting database seeding...\n")
    
    db = SessionLocal()
    
    try:
        # Create data in order
        subjects = seed_subjects(db)
        print()
        
        students = seed_students(db)
        print()
        
        companies = seed_companies(db)
        print()
        
        seed_jobs(db, companies)
        print()
        
        print("✅ Database seeding completed successfully!\n")
        print("📊 Summary:")
        print(f"   - Subjects: {len(subjects)}")
        print(f"   - Students: {len(students)}")
        print(f"   - Companies: {len(companies)}")
        print(f"   - Jobs: 3")
        print("\n🚀 You can now test the API!")
        print("   - Access docs at: http://localhost:8000/docs")
        print("   - Test matching at: http://localhost:8000/api/v1/matching/student/1/recommended-jobs\n")
        
    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_all()
