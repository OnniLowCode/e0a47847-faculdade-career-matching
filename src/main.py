"""
Faculty Career Matching System - Main Application
Sistema que conecta notas da grade curricular com empresas parceiras
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config.database import engine, Base
from src.api.routes import (
    student_routes,
    company_routes,
    job_routes,
    subject_routes,
    matching_routes,
    integrations_routes
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="Faculty Career Matching System",
    description="""
    ## Sistema Inteligente de Matching entre Alunos e Empresas
    
    Este sistema conecta o desempenho acadêmico dos alunos (notas por disciplina) 
    com oportunidades de emprego de empresas parceiras da faculdade.
    
    ### Funcionalidades Principais:
    
    * **👨‍🎓 Gestão de Alunos**: Cadastro de alunos, notas por disciplina, cálculo automático de GPA
    * **🏢 Gestão de Empresas**: Cadastro de empresas parceiras e vagas de emprego
    * **📊 Grade Curricular**: Gestão de disciplinas e desempenho acadêmico
    * **🎯 Matching Inteligente**: Algoritmo que identifica os melhores matches entre alunos e vagas
    * **📈 Analytics**: Estatísticas e insights sobre candidatos e oportunidades
    
    ### Algoritmo de Matching:
    
    O sistema utiliza um algoritmo ponderado que considera:
    - **55%** Disciplinas Específicas (notas em matérias requeridas pela vaga)
    - **20%** GPA Geral (média geral do aluno)
    - **15%** Compatibilidade de Curso
    - **10%** Semestre Mínimo
    
    ### Casos de Uso:
    
    1. **Para Alunos**: Descobrir vagas compatíveis com seu perfil acadêmico
    2. **Para Empresas**: Encontrar candidatos qualificados com base em critérios acadêmicos
    3. **Para Coordenadores**: Analisar desempenho e oportunidades disponíveis
    
    """,
    version="1.0.0",
    contact={
        "name": "Faculty Career Matching Support",
        "email": "support@facultycareer.com"
    }
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(student_routes.router, prefix="/api/v1")
app.include_router(company_routes.router, prefix="/api/v1")
app.include_router(job_routes.router, prefix="/api/v1")
app.include_router(subject_routes.router, prefix="/api/v1")
app.include_router(matching_routes.router, prefix="/api/v1")
app.include_router(integrations_routes.router, prefix="/api/v1")


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - Welcome message
    """
    return {
        "message": "Welcome to Faculty Career Matching System",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "description": "Sistema que conecta notas da grade curricular com empresas parceiras"
    }


@app.get("/health", tags=["Health"])
async def health():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "service": "Faculty Career Matching System"
    }


@app.get("/api/v1/info", tags=["Info"])
async def api_info():
    """
    API Information and available endpoints
    """
    return {
        "api_version": "1.0.0",
        "endpoints": {
            "students": {
                "base": "/api/v1/students",
                "description": "Gestão de alunos e notas",
                "operations": ["create", "list", "get", "update", "delete", "add_grades"]
            },
            "companies": {
                "base": "/api/v1/companies",
                "description": "Gestão de empresas parceiras",
                "operations": ["create", "list", "get", "update"]
            },
            "jobs": {
                "base": "/api/v1/jobs",
                "description": "Gestão de vagas de emprego",
                "operations": ["create", "list", "get", "update", "delete", "apply"]
            },
            "subjects": {
                "base": "/api/v1/subjects",
                "description": "Gestão de disciplinas da grade curricular",
                "operations": ["create", "bulk_create", "list", "get", "update", "delete"]
            },
            "matching": {
                "base": "/api/v1/matching",
                "description": "Sistema inteligente de matching",
                "operations": [
                    "recommended_jobs_for_student",
                    "recommended_candidates_for_job",
                    "calculate_match_score",
                    "analytics"
                ]
            }
        },
        "features": {
            "intelligent_matching": "Algoritmo de matching baseado em desempenho acadêmico",
            "automatic_gpa": "Cálculo automático de GPA ao adicionar notas",
            "subject_requirements": "Requisitos específicos por disciplina para cada vaga",
            "analytics": "Estatísticas e insights detalhados"
        }
    }
