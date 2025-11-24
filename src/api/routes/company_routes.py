"""
Company API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from src.config.database import get_db
from src.services.job_service import CompanyService
from src.schemas.company import CompanyCreate, CompanyUpdate, CompanyResponse, CompanyDetailResponse

router = APIRouter(prefix="/companies", tags=["Companies"])


@router.post("", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
def create_company(
    company_data: CompanyCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new company account
    
    - **email**: Company's email (will be used for login)
    - **password**: Password for the account
    - **company_name**: Official company name
    - **cnpj**: Brazilian company registration number (optional)
    - **industry**: Industry/sector
    """
    service = CompanyService(db)
    
    try:
        company = service.create_company(company_data)
        
        # Build response
        response = CompanyResponse.model_validate(company)
        response.email = company.user.email if company.user else ""
        
        return response
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("", response_model=List[CompanyResponse])
def list_companies(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List all registered companies
    """
    service = CompanyService(db)
    companies = service.list_companies(skip=skip, limit=limit)
    
    # Build responses
    responses = []
    for company in companies:
        response = CompanyResponse.model_validate(company)
        response.email = company.user.email if company.user else ""
        responses.append(response)
    
    return responses


@router.get("/{company_id}", response_model=CompanyDetailResponse)
def get_company(
    company_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed company information
    """
    service = CompanyService(db)
    company = service.get_company_by_id(company_id)
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    # Build detailed response
    from src.models.models import JobStatus
    
    response = CompanyDetailResponse.model_validate(company)
    response.email = company.user.email if company.user else ""
    response.total_jobs = len(company.jobs)
    response.active_jobs = len([j for j in company.jobs if j.status == JobStatus.OPEN])
    
    return response


@router.put("/{company_id}", response_model=CompanyResponse)
def update_company(
    company_id: int,
    company_data: CompanyUpdate,
    db: Session = Depends(get_db)
):
    """
    Update company profile
    """
    service = CompanyService(db)
    company = service.update_company(company_id, company_data)
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    response = CompanyResponse.model_validate(company)
    response.email = company.user.email if company.user else ""
    
    return response
