"""
External API Integrations Routes
Integrates with free APIs to enrich the system
"""
from fastapi import APIRouter, HTTPException, Query
import requests
from typing import Optional

router = APIRouter(prefix="/integrations", tags=["External Integrations"])


@router.get("/github/user/{username}")
async def get_github_profile(username: str):
    """
    Fetch GitHub profile data for a student
    
    **Free API**: https://api.github.com
    - No authentication required for basic data
    - Rate limit: 60 requests/hour (unauthenticated)
    
    Returns:
    - Public repositories count
    - Followers/Following
    - Bio and company
    - Account creation date
    """
    try:
        response = requests.get(
            f"https://api.github.com/users/{username}",
            timeout=10
        )
        
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="GitHub user not found")
        
        response.raise_for_status()
        data = response.json()
        
        return {
            "username": data.get("login"),
            "name": data.get("name"),
            "bio": data.get("bio"),
            "company": data.get("company"),
            "location": data.get("location"),
            "email": data.get("email"),
            "public_repos": data.get("public_repos", 0),
            "followers": data.get("followers", 0),
            "following": data.get("following", 0),
            "created_at": data.get("created_at"),
            "profile_url": data.get("html_url"),
            "avatar_url": data.get("avatar_url")
        }
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"GitHub API error: {str(e)}")


@router.get("/github/languages/{username}")
async def get_github_languages(username: str, limit: int = Query(10, ge=1, le=100)):
    """
    Analyze programming languages used in student's GitHub repositories
    
    Useful for matching students with jobs requiring specific tech stacks
    
    **Returns**: Dictionary with language usage frequency
    """
    try:
        # Get user's repositories
        repos_response = requests.get(
            f"https://api.github.com/users/{username}/repos",
            params={"per_page": limit, "sort": "updated"},
            timeout=10
        )
        repos_response.raise_for_status()
        repos = repos_response.json()
        
        # Count languages
        languages = {}
        total_repos = 0
        
        for repo in repos:
            if not repo.get("fork"):  # Ignore forks
                total_repos += 1
                lang = repo.get("language")
                if lang:
                    languages[lang] = languages.get(lang, 0) + 1
        
        # Calculate percentages
        language_stats = {
            lang: {
                "count": count,
                "percentage": round((count / total_repos) * 100, 2) if total_repos > 0 else 0
            }
            for lang, count in sorted(languages.items(), key=lambda x: x[1], reverse=True)
        }
        
        return {
            "username": username,
            "total_repos_analyzed": total_repos,
            "languages": language_stats,
            "top_language": max(languages.items(), key=lambda x: x[1])[0] if languages else None
        }
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"GitHub API error: {str(e)}")


@router.get("/cnpj/{cnpj}")
async def validate_cnpj(cnpj: str):
    """
    Validate and enrich company data using Brazilian CNPJ
    
    **Free API**: https://brasilapi.com.br
    - Unlimited requests
    - Official government data
    
    Returns complete company information including:
    - Company name and fantasy name
    - Full address
    - Economic activity (CNAE)
    - Registration status
    """
    # Clean CNPJ (remove formatting)
    cnpj_clean = cnpj.replace(".", "").replace("/", "").replace("-", "").strip()
    
    if len(cnpj_clean) != 14:
        raise HTTPException(status_code=400, detail="Invalid CNPJ format. Must be 14 digits")
    
    try:
        response = requests.get(
            f"https://brasilapi.com.br/api/cnpj/v1/{cnpj_clean}",
            timeout=10
        )
        
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="CNPJ not found")
        
        response.raise_for_status()
        data = response.json()
        
        return {
            "cnpj": cnpj_clean,
            "company_name": data.get("razao_social"),
            "fantasy_name": data.get("nome_fantasia"),
            "opening_date": data.get("data_inicio_atividade"),
            "registration_status": data.get("descricao_situacao_cadastral"),
            "activity": {
                "code": data.get("cnae_fiscal"),
                "description": data.get("cnae_fiscal_descricao")
            },
            "address": {
                "street": data.get("logradouro"),
                "number": data.get("numero"),
                "complement": data.get("complemento"),
                "neighborhood": data.get("bairro"),
                "city": data.get("municipio"),
                "state": data.get("uf"),
                "zip_code": data.get("cep")
            },
            "contact": {
                "email": data.get("email"),
                "phone": data.get("ddd_telefone_1")
            },
            "size": {
                "capital": data.get("capital_social"),
                "type": data.get("porte")
            }
        }
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Brasil API error: {str(e)}")


@router.get("/cep/{cep}")
async def get_address_by_cep(cep: str):
    """
    Get address information from Brazilian ZIP code (CEP)
    
    **Free API**: https://viacep.com.br
    - Unlimited requests
    - Instant autocomplete for addresses
    
    Useful for auto-filling company addresses
    """
    # Clean CEP
    cep_clean = cep.replace("-", "").replace(".", "").strip()
    
    if len(cep_clean) != 8:
        raise HTTPException(status_code=400, detail="Invalid CEP format. Must be 8 digits")
    
    try:
        response = requests.get(
            f"https://viacep.com.br/ws/{cep_clean}/json/",
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        if data.get("erro"):
            raise HTTPException(status_code=404, detail="CEP not found")
        
        return {
            "cep": data.get("cep"),
            "street": data.get("logradouro"),
            "complement": data.get("complemento"),
            "neighborhood": data.get("bairro"),
            "city": data.get("localidade"),
            "state": data.get("uf"),
            "ibge_code": data.get("ibge"),
            "ddd": data.get("ddd")
        }
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"ViaCEP API error: {str(e)}")


@router.get("/email/validate")
async def validate_email(email: str):
    """
    Validate email address format and check if it exists
    
    **Note**: This is a basic validation. For production, use a service like:
    - Abstract Email Validation API (100 free/month)
    - Hunter.io (50 free/month)
    - MailboxValidator
    
    This endpoint does basic format validation.
    """
    import re
    
    # Basic email regex validation
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    is_valid_format = bool(re.match(email_regex, email))
    
    if not is_valid_format:
        return {
            "email": email,
            "valid": False,
            "reason": "Invalid email format"
        }
    
    # Extract domain
    domain = email.split("@")[1]
    
    # Check if it's a common disposable email domain
    disposable_domains = [
        "tempmail.com", "10minutemail.com", "guerrillamail.com",
        "mailinator.com", "throwaway.email"
    ]
    
    is_disposable = domain in disposable_domains
    
    # Educational email detection
    is_educational = domain.endswith(".edu") or domain.endswith(".edu.br")
    
    return {
        "email": email,
        "valid": is_valid_format,
        "format_valid": is_valid_format,
        "domain": domain,
        "is_disposable": is_disposable,
        "is_educational": is_educational,
        "recommendation": "Accept" if is_valid_format and not is_disposable else "Review"
    }


@router.get("/linkedin/extract-id")
async def extract_linkedin_id(profile_url: str):
    """
    Extract LinkedIn ID from profile URL
    
    **Input**: https://linkedin.com/in/username or https://www.linkedin.com/in/username
    **Output**: username
    
    Useful for storing and validating LinkedIn profiles
    """
    import re
    
    # Extract username from LinkedIn URL
    patterns = [
        r'linkedin\.com/in/([a-zA-Z0-9-]+)',
        r'linkedin\.com/profile/([a-zA-Z0-9-]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, profile_url)
        if match:
            username = match.group(1)
            return {
                "original_url": profile_url,
                "username": username,
                "clean_url": f"https://linkedin.com/in/{username}",
                "valid": True
            }
    
    return {
        "original_url": profile_url,
        "valid": False,
        "error": "Could not extract LinkedIn username from URL"
    }


@router.get("/salary/benchmark")
async def get_salary_benchmark(
    job_title: str,
    location: Optional[str] = "Brasil",
    experience_level: Optional[str] = "junior"
):
    """
    Get salary benchmark data for tech positions in Brazil
    
    **Note**: This is mock data. For production, integrate with:
    - Glassdoor API (limited free tier)
    - levels.fyi API
    - SERPAPI for Google Jobs data
    
    Returns estimated salary ranges based on position and experience
    """
    # Mock salary data for Brazilian tech market (in BRL)
    salary_data = {
        "developer": {
            "junior": {"min": 3000, "max": 6000, "avg": 4500},
            "mid": {"min": 6000, "max": 10000, "avg": 8000},
            "senior": {"min": 10000, "max": 18000, "avg": 14000}
        },
        "backend": {
            "junior": {"min": 3500, "max": 6500, "avg": 5000},
            "mid": {"min": 7000, "max": 12000, "avg": 9500},
            "senior": {"min": 12000, "max": 20000, "avg": 16000}
        },
        "frontend": {
            "junior": {"min": 3000, "max": 5500, "avg": 4200},
            "mid": {"min": 6000, "max": 10000, "avg": 8000},
            "senior": {"min": 10000, "max": 16000, "avg": 13000}
        },
        "fullstack": {
            "junior": {"min": 4000, "max": 7000, "avg": 5500},
            "mid": {"min": 8000, "max": 13000, "avg": 10500},
            "senior": {"min": 13000, "max": 22000, "avg": 17500}
        },
        "data": {
            "junior": {"min": 4000, "max": 7000, "avg": 5500},
            "mid": {"min": 8000, "max": 14000, "avg": 11000},
            "senior": {"min": 14000, "max": 25000, "avg": 19500}
        }
    }
    
    # Simple keyword matching
    job_key = "developer"
    title_lower = job_title.lower()
    
    if "backend" in title_lower or "back-end" in title_lower:
        job_key = "backend"
    elif "frontend" in title_lower or "front-end" in title_lower:
        job_key = "frontend"
    elif "fullstack" in title_lower or "full-stack" in title_lower:
        job_key = "fullstack"
    elif "data" in title_lower or "dados" in title_lower:
        job_key = "data"
    
    exp_level = experience_level.lower()
    if "senior" in exp_level or "sênior" in exp_level:
        exp_key = "senior"
    elif "pleno" in exp_level or "mid" in exp_level:
        exp_key = "mid"
    else:
        exp_key = "junior"
    
    salary_info = salary_data.get(job_key, {}).get(exp_key, {"min": 3000, "max": 6000, "avg": 4500})
    
    return {
        "job_title": job_title,
        "normalized_title": job_key,
        "experience_level": exp_key,
        "location": location,
        "currency": "BRL",
        "salary_range": {
            "minimum": salary_info["min"],
            "maximum": salary_info["max"],
            "average": salary_info["avg"]
        },
        "formatted_range": f"R$ {salary_info['min']:,} - R$ {salary_info['max']:,}",
        "data_source": "Market estimates for Brazil tech market (2024)",
        "note": "This is estimated data. For production, integrate with real salary APIs"
    }


@router.get("/tech-skills/trending")
async def get_trending_tech_skills():
    """
    Get trending tech skills and technologies
    
    **Note**: This is based on common industry trends. For real-time data, integrate with:
    - GitHub Trending API
    - Stack Overflow Trends
    - LinkedIn Skills API
    
    Useful for students to know which skills to develop
    """
    return {
        "last_updated": "2024",
        "categories": {
            "programming_languages": {
                "trending": ["Python", "TypeScript", "Go", "Rust", "Kotlin"],
                "stable": ["JavaScript", "Java", "C++", "C#", "PHP"],
                "demand_rating": {
                    "Python": 10,
                    "JavaScript": 10,
                    "TypeScript": 9,
                    "Java": 9,
                    "Go": 8,
                    "Rust": 7
                }
            },
            "frameworks": {
                "web": ["React", "Next.js", "Vue.js", "Angular", "Svelte"],
                "backend": ["FastAPI", "Django", "Node.js", "Spring Boot", "Express"],
                "mobile": ["React Native", "Flutter", "Swift", "Kotlin"]
            },
            "databases": {
                "sql": ["PostgreSQL", "MySQL", "SQL Server"],
                "nosql": ["MongoDB", "Redis", "Cassandra", "DynamoDB"]
            },
            "cloud_platforms": {
                "top": ["AWS", "Google Cloud", "Azure", "Vercel", "Heroku"],
                "demand_rating": {
                    "AWS": 10,
                    "Google Cloud": 8,
                    "Azure": 9,
                    "Docker": 10,
                    "Kubernetes": 9
                }
            },
            "tools": {
                "version_control": ["Git", "GitHub", "GitLab"],
                "ci_cd": ["GitHub Actions", "Jenkins", "GitLab CI"],
                "containers": ["Docker", "Kubernetes", "Docker Compose"]
            }
        },
        "top_10_most_demanded": [
            "Python",
            "JavaScript/TypeScript",
            "React",
            "Docker",
            "AWS",
            "SQL/PostgreSQL",
            "Git",
            "Node.js",
            "API Development",
            "Agile/Scrum"
        ]
    }
