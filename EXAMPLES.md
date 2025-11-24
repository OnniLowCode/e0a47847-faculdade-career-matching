# 🚀 Exemplos Práticos de Uso da API

## 📌 Base URL

Todos os exemplos assumem que a API está rodando em:
```
http://localhost:8006
```

Documentação interativa disponível em:
- Swagger UI: http://localhost:8006/docs
- ReDoc: http://localhost:8006/redoc

---

## 🌱 1. Inicialização com Dados de Exemplo

### Carregar dados de teste

```bash
# Dentro do container Docker
docker exec -it faculdade_career_matching-app python -m src.utils.seed_data

# Ou localmente
python -m src.utils.seed_data
```

Isso criará:
- 10 disciplinas (Ciência da Computação)
- 3 estudantes com notas
- 3 empresas parceiras
- 3 vagas de emprego

---

## 👨‍🎓 2. Gestão de Alunos

### 2.1 Criar Novo Aluno

```bash
curl -X POST "http://localhost:8006/api/v1/students" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "carlos.mendes@university.edu",
    "password": "senha123",
    "registration_number": "2024005",
    "full_name": "Carlos Mendes",
    "course": "Ciência da Computação",
    "semester": 4,
    "phone": "+5511988887777",
    "linkedin_url": "https://linkedin.com/in/carlosmendes",
    "github_url": "https://github.com/carlosmendes",
    "bio": "Desenvolvedor backend focado em Python e APIs",
    "skills": "Python, FastAPI, PostgreSQL, Docker"
  }'
```

**Resposta:**
```json
{
  "full_name": "Carlos Mendes",
  "course": "Ciência da Computação",
  "semester": 4,
  "phone": "+5511988887777",
  "linkedin_url": "https://linkedin.com/in/carlosmendes",
  "github_url": "https://github.com/carlosmendes",
  "portfolio_url": null,
  "bio": "Desenvolvedor backend focado em Python e APIs",
  "skills": "Python, FastAPI, PostgreSQL, Docker",
  "id": 4,
  "registration_number": "2024005",
  "gpa": 0.0,
  "email": "carlos.mendes@university.edu",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### 2.2 Adicionar Notas

```bash
# Adicionar nota em Banco de Dados (subject_id = 4)
curl -X POST "http://localhost:8006/api/v1/students/4/grades" \
  -H "Content-Type: application/json" \
  -d '{
    "subject_id": 4,
    "grade": 9.5,
    "semester_year": "2024.1"
  }'

# Adicionar nota em Desenvolvimento Web (subject_id = 5)
curl -X POST "http://localhost:8006/api/v1/students/4/grades" \
  -H "Content-Type: application/json" \
  -d '{
    "subject_id": 5,
    "grade": 8.7,
    "semester_year": "2024.1"
  }'
```

### 2.3 Ver Perfil Completo do Aluno

```bash
curl "http://localhost:8006/api/v1/students/4"
```

### 2.4 Ver Performance Acadêmica

```bash
curl "http://localhost:8006/api/v1/students/4/performance"
```

**Resposta:**
```json
{
  "student_id": 4,
  "gpa": 9.1,
  "total_subjects": 2,
  "category_averages": {
    "database": 9.5,
    "web": 8.7
  },
  "best_category": "database",
  "grades_distribution": {
    "excellent (9-10)": 2,
    "good (7-8.9)": 0,
    "average (5-6.9)": 0,
    "below_average (<5)": 0
  }
}
```

---

## 🏢 3. Gestão de Empresas

### 3.1 Criar Nova Empresa

```bash
curl -X POST "http://localhost:8006/api/v1/companies" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "rh@innovatech.com",
    "password": "senha123",
    "company_name": "InnovaTech Solutions",
    "cnpj": "33.444.555/0001-66",
    "industry": "Software Development",
    "size": "11-50",
    "website": "https://innovatech.com",
    "description": "Consultoria e desenvolvimento de software personalizado",
    "city": "Curitiba",
    "state": "PR",
    "phone": "+5541988880000",
    "contact_email": "contato@innovatech.com"
  }'
```

### 3.2 Listar Empresas

```bash
curl "http://localhost:8006/api/v1/companies"
```

### 3.3 Ver Detalhes da Empresa

```bash
curl "http://localhost:8006/api/v1/companies/1"
```

---

## 💼 4. Gestão de Vagas

### 4.1 Criar Vaga com Requisitos Específicos

```bash
curl -X POST "http://localhost:8006/api/v1/jobs?company_id=1" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Desenvolvedor Python Júnior",
    "description": "Procuramos desenvolvedor Python para atuar em projetos de APIs REST e automação",
    "requirements": "Conhecimento sólido em Python, experiência com bancos de dados relacionais, versionamento Git",
    "responsibilities": "Desenvolver e manter APIs REST, realizar code reviews, participar de sprints ágeis",
    "benefits": "Vale refeição R$ 30/dia, plano de saúde, home office 2x/semana",
    "salary_range": "R$ 4.000 - R$ 6.000",
    "location": "São Paulo, SP (Híbrido)",
    "work_type": "hybrid",
    "job_type": "junior",
    "minimum_gpa": 7.5,
    "minimum_semester": 4,
    "preferred_courses": "[\"Ciência da Computação\", \"Engenharia de Software\", \"Sistemas de Informação\"]",
    "vacancies": 2,
    "subject_requirements": [
      {
        "subject_id": 1,
        "minimum_grade": 7.0,
        "weight": 1.5,
        "is_mandatory": true
      },
      {
        "subject_id": 4,
        "minimum_grade": 8.0,
        "weight": 2.0,
        "is_mandatory": true
      },
      {
        "subject_id": 3,
        "minimum_grade": 7.0,
        "weight": 1.0,
        "is_mandatory": false
      }
    ]
  }'
```

**Explicação dos requisitos:**
- `subject_id: 1` - Introdução à Programação (nota mínima 7.0, peso 1.5, obrigatório)
- `subject_id: 4` - Banco de Dados (nota mínima 8.0, peso 2.0, obrigatório)
- `subject_id: 3` - POO (nota mínima 7.0, peso 1.0, não obrigatório)

### 4.2 Listar Vagas Abertas

```bash
curl "http://localhost:8006/api/v1/jobs?status_filter=open"
```

### 4.3 Buscar Vagas Remotas

```bash
curl "http://localhost:8006/api/v1/jobs?work_type=remote"
```

### 4.4 Buscar Estágios

```bash
curl "http://localhost:8006/api/v1/jobs?job_type=internship"
```

---

## 🎯 5. Sistema de Matching (PRINCIPAL)

### 5.1 Vagas Recomendadas para um Aluno

```bash
curl "http://localhost:8006/api/v1/matching/student/1/recommended-jobs?min_score=50&limit=10"
```

**Resposta Exemplo:**
```json
[
  {
    "job_id": 1,
    "job_title": "Desenvolvedor Backend Júnior",
    "company_name": "Tech Solutions Brasil",
    "match_score": 85.5,
    "match_percentage": 92.3,
    "location": "São Paulo, SP (Híbrido)",
    "work_type": "hybrid",
    "salary_range": "R$ 3.500 - R$ 5.000",
    "matched_subjects": [
      {
        "subject_id": 4,
        "subject_code": "CS202",
        "subject_name": "Banco de Dados",
        "required_grade": 7.5,
        "weight": 2.0,
        "is_mandatory": true,
        "student_grade": 8.5,
        "met": true,
        "grade_excess": 1.0
      },
      {
        "subject_id": 3,
        "subject_code": "CS201",
        "subject_name": "Programação Orientada a Objetos",
        "required_grade": 7.0,
        "weight": 1.5,
        "is_mandatory": true,
        "student_grade": 9.0,
        "met": true,
        "grade_excess": 2.0
      }
    ],
    "missing_subjects": [],
    "gpa_match": true,
    "semester_match": true,
    "course_match": true,
    "recommendation_reason": "GPA (8.9) meets requirement; Course matches preferred courses; 3/3 required subjects met (100%)"
  },
  {
    "job_id": 2,
    "job_title": "Estágio em Desenvolvimento Web",
    "company_name": "StartupAI",
    "match_score": 78.2,
    "match_percentage": 85.1,
    "location": "São Paulo, SP (Remoto)",
    "work_type": "remote",
    "salary_range": "R$ 1.500 - R$ 2.000",
    "matched_subjects": [
      {
        "subject_id": 5,
        "subject_code": "CS301",
        "subject_name": "Desenvolvimento Web",
        "required_grade": 7.0,
        "weight": 2.0,
        "is_mandatory": true,
        "student_grade": 9.2,
        "met": true,
        "grade_excess": 2.2
      }
    ],
    "missing_subjects": [],
    "gpa_match": true,
    "semester_match": true,
    "course_match": true,
    "recommendation_reason": "GPA (8.9) exceeds requirement; 2/2 required subjects met (100%)"
  }
]
```

### 5.2 Candidatos Recomendados para uma Vaga

```bash
curl "http://localhost:8006/api/v1/matching/job/1/recommended-candidates?min_score=60&limit=20"
```

**Resposta Exemplo:**
```json
{
  "job_id": 1,
  "job_title": "Desenvolvedor Backend Júnior",
  "company_name": "Tech Solutions Brasil",
  "total_candidates": 3,
  "candidates": [
    {
      "student_id": 2,
      "student_name": "Maria Santos",
      "registration_number": "2021002",
      "course": "Ciência da Computação",
      "semester": 6,
      "gpa": 9.3,
      "match_score": 91.2,
      "match_percentage": 94.5,
      "matched_subjects": [
        {
          "subject_code": "CS202",
          "subject_name": "Banco de Dados",
          "student_grade": 9.0,
          "required_grade": 7.5,
          "met": true
        },
        {
          "subject_code": "CS201",
          "student_grade": 9.8,
          "required_grade": 7.0,
          "met": true
        }
      ],
      "missing_subjects": [],
      "email": "maria.santos@university.edu"
    },
    {
      "student_id": 1,
      "student_name": "João Silva",
      "registration_number": "2021001",
      "course": "Ciência da Computação",
      "semester": 5,
      "gpa": 8.9,
      "match_score": 85.5,
      "match_percentage": 88.2,
      "matched_subjects": [...],
      "missing_subjects": [],
      "email": "joao.silva@university.edu"
    }
  ]
}
```

### 5.3 Calcular Match Específico

```bash
curl "http://localhost:8006/api/v1/matching/calculate/1/1"
```

**Resposta Detalhada:**
```json
{
  "student": {
    "id": 1,
    "name": "João Silva",
    "course": "Ciência da Computação",
    "semester": 5,
    "gpa": 8.9
  },
  "job": {
    "id": 1,
    "title": "Desenvolvedor Backend Júnior",
    "company": "Tech Solutions Brasil"
  },
  "match_percentage": 88.2,
  "details": {
    "student_id": 1,
    "job_id": 1,
    "student_name": "João Silva",
    "job_title": "Desenvolvedor Backend Júnior",
    "calculated_at": "2024-01-15T14:30:00",
    "gpa_match": true,
    "student_gpa": 8.9,
    "required_gpa": 7.0,
    "semester_match": true,
    "student_semester": 5,
    "required_semester": 4,
    "course_match": true,
    "student_course": "Ciência da Computação",
    "preferred_courses": "[\"Ciência da Computação\", \"Engenharia de Software\"]",
    "matched_subjects": [...],
    "missing_subjects": [],
    "subject_match_percentage": 100.0,
    "final_score": 88.2,
    "raw_score": 85.5,
    "max_possible_score": 100.0,
    "recommendation_reason": "GPA (8.9) meets requirement; Course matches preferred courses; 3/3 required subjects met (100%)"
  }
}
```

### 5.4 Analytics de Matching para Aluno

```bash
curl "http://localhost:8006/api/v1/matching/analytics/student/1"
```

### 5.5 Analytics de Matching para Vaga

```bash
curl "http://localhost:8006/api/v1/matching/analytics/job/1"
```

---

## 🔗 6. Integrações com APIs Externas

### 6.1 Buscar Perfil do GitHub

```bash
curl "http://localhost:8006/api/v1/integrations/github/user/joaosilva"
```

**Resposta:**
```json
{
  "username": "joaosilva",
  "name": "João Silva",
  "bio": "Full-stack developer passionate about Python and JavaScript",
  "company": "Tech Solutions",
  "location": "São Paulo, Brazil",
  "email": "joao@example.com",
  "public_repos": 42,
  "followers": 128,
  "following": 85,
  "created_at": "2019-03-15T10:30:00Z",
  "profile_url": "https://github.com/joaosilva",
  "avatar_url": "https://avatars.githubusercontent.com/..."
}
```

### 6.2 Analisar Linguagens do GitHub

```bash
curl "http://localhost:8006/api/v1/integrations/github/languages/joaosilva?limit=10"
```

**Resposta:**
```json
{
  "username": "joaosilva",
  "total_repos_analyzed": 10,
  "languages": {
    "Python": {
      "count": 6,
      "percentage": 60.0
    },
    "JavaScript": {
      "count": 3,
      "percentage": 30.0
    },
    "TypeScript": {
      "count": 1,
      "percentage": 10.0
    }
  },
  "top_language": "Python"
}
```

### 6.3 Validar CNPJ de Empresa

```bash
curl "http://localhost:8006/api/v1/integrations/cnpj/12.345.678/0001-90"
```

**Resposta:**
```json
{
  "cnpj": "12345678000190",
  "company_name": "TECH SOLUTIONS BRASIL LTDA",
  "fantasy_name": "Tech Solutions",
  "opening_date": "2015-06-10",
  "registration_status": "ATIVA",
  "activity": {
    "code": "6201-5/00",
    "description": "Desenvolvimento de programas de computador sob encomenda"
  },
  "address": {
    "street": "Avenida Paulista",
    "number": "1500",
    "complement": "Sala 1001",
    "neighborhood": "Bela Vista",
    "city": "São Paulo",
    "state": "SP",
    "zip_code": "01310-100"
  },
  "contact": {
    "email": "contato@techsolutions.com.br",
    "phone": "1133334444"
  },
  "size": {
    "capital": "500000.00",
    "type": "DEMAIS"
  }
}
```

### 6.4 Buscar Endereço por CEP

```bash
curl "http://localhost:8006/api/v1/integrations/cep/01310-100"
```

### 6.5 Validar Email

```bash
curl "http://localhost:8006/api/v1/integrations/email/validate?email=joao.silva@university.edu"
```

**Resposta:**
```json
{
  "email": "joao.silva@university.edu",
  "valid": true,
  "format_valid": true,
  "domain": "university.edu",
  "is_disposable": false,
  "is_educational": true,
  "recommendation": "Accept"
}
```

### 6.6 Benchmark de Salários

```bash
curl "http://localhost:8006/api/v1/integrations/salary/benchmark?job_title=Desenvolvedor%20Backend&experience_level=junior"
```

**Resposta:**
```json
{
  "job_title": "Desenvolvedor Backend",
  "normalized_title": "backend",
  "experience_level": "junior",
  "location": "Brasil",
  "currency": "BRL",
  "salary_range": {
    "minimum": 3500,
    "maximum": 6500,
    "average": 5000
  },
  "formatted_range": "R$ 3,500 - R$ 6,500",
  "data_source": "Market estimates for Brazil tech market (2024)"
}
```

### 6.7 Skills em Tendência

```bash
curl "http://localhost:8006/api/v1/integrations/tech-skills/trending"
```

---

## 📝 7. Candidaturas

### 7.1 Aluno se Candidata a uma Vaga

```bash
curl -X POST "http://localhost:8006/api/v1/jobs/applications?student_id=1" \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": 1,
    "cover_letter": "Tenho grande interesse nesta vaga pois meu perfil acadêmico está alinhado com os requisitos. Possuo experiência prática com Python e bancos de dados através de projetos acadêmicos."
  }'
```

**Nota:** O sistema calcula automaticamente o `match_score` antes de criar a candidatura!

### 7.2 Ver Candidaturas de um Aluno

```bash
curl "http://localhost:8006/api/v1/jobs/applications/student/1"
```

### 7.3 Ver Candidaturas de uma Vaga

```bash
curl "http://localhost:8006/api/v1/jobs/1/applications"
```

### 7.4 Atualizar Status da Candidatura

```bash
curl -X PATCH "http://localhost:8006/api/v1/jobs/applications/1" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "interview"
  }'
```

**Status possíveis:**
- `pending` - Pendente de análise
- `approved` - Aprovado
- `rejected` - Rejeitado
- `interview` - Convocado para entrevista

---

## 📚 8. Gestão de Disciplinas

### 8.1 Criar Disciplina

```bash
curl -X POST "http://localhost:8006/api/v1/subjects" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "CS401",
    "name": "Inteligência Artificial",
    "course": "Ciência da Computação",
    "semester": 7,
    "credits": 4,
    "description": "Fundamentos de IA e Machine Learning",
    "category": "ai"
  }'
```

### 8.2 Criar Múltiplas Disciplinas

```bash
curl -X POST "http://localhost:8006/api/v1/subjects/bulk" \
  -H "Content-Type: application/json" \
  -d '[
    {
      "code": "CS402",
      "name": "Deep Learning",
      "course": "Ciência da Computação",
      "semester": 8,
      "credits": 4,
      "category": "ai"
    },
    {
      "code": "CS403",
      "name": "Processamento de Linguagem Natural",
      "course": "Ciência da Computação",
      "semester": 8,
      "credits": 3,
      "category": "ai"
    }
  ]'
```

### 8.3 Listar Disciplinas por Curso

```bash
curl "http://localhost:8006/api/v1/subjects?course=Ciência%20da%20Computação"
```

### 8.4 Ver Estatísticas de uma Disciplina

```bash
curl "http://localhost:8006/api/v1/subjects/1/statistics"
```

**Resposta:**
```json
{
  "subject_id": 1,
  "subject_code": "CS101",
  "subject_name": "Introdução à Programação",
  "total_students": 3,
  "average_grade": 8.2,
  "highest_grade": 10.0,
  "lowest_grade": 7.0,
  "distribution": {
    "excellent (9-10)": 1,
    "good (7-8.9)": 2,
    "average (5-6.9)": 0,
    "below_average (<5)": 0
  }
}
```

---

## 🧪 9. Testes e Debugging

### 9.1 Health Check

```bash
curl "http://localhost:8006/health"
```

### 9.2 Informações da API

```bash
curl "http://localhost:8006/api/v1/info"
```

---

## 💡 10. Casos de Uso Completos

### Caso 1: Empresa Busca Candidatos

```bash
# 1. Criar empresa
curl -X POST "http://localhost:8006/api/v1/companies" -H "Content-Type: application/json" -d '{...}'

# 2. Criar vaga com requisitos
curl -X POST "http://localhost:8006/api/v1/jobs?company_id=1" -H "Content-Type: application/json" -d '{...}'

# 3. Buscar candidatos recomendados
curl "http://localhost:8006/api/v1/matching/job/1/recommended-candidates?min_score=70"

# 4. Ver candidaturas recebidas
curl "http://localhost:8006/api/v1/jobs/1/applications"
```

### Caso 2: Aluno Busca Oportunidades

```bash
# 1. Criar perfil
curl -X POST "http://localhost:8006/api/v1/students" -H "Content-Type: application/json" -d '{...}'

# 2. Adicionar notas
curl -X POST "http://localhost:8006/api/v1/students/1/grades" -H "Content-Type: application/json" -d '{...}'

# 3. Ver vagas recomendadas
curl "http://localhost:8006/api/v1/matching/student/1/recommended-jobs?min_score=50"

# 4. Candidatar-se
curl -X POST "http://localhost:8006/api/v1/jobs/applications?student_id=1" -H "Content-Type: application/json" -d '{...}'

# 5. Acompanhar candidaturas
curl "http://localhost:8006/api/v1/jobs/applications/student/1"
```

---

## 🎯 Dicas de Uso

1. **Match Score Mínimo**: 
   - Para vagas júnior: `min_score=50`
   - Para vagas pleno: `min_score=70`
   - Para vagas sênior: `min_score=80`

2. **Pesos das Disciplinas**:
   - Use `weight=2.0` para disciplinas críticas
   - Use `weight=1.0` para disciplinas desejáveis
   - Use `is_mandatory=true` apenas para requisitos essenciais

3. **Enrichment de Dados**:
   - Use a API do GitHub para validar portfólios
   - Use Brasil API para validar CNPJs
   - Use ViaCEP para autocompletar endereços

---

## 📞 Próximos Passos

1. Teste os endpoints no Swagger UI: http://localhost:8006/docs
2. Carregue os dados de exemplo com o seed script
3. Experimente diferentes combinações de matching
4. Integre com sistemas externos usando as rotas de integração

**Happy Coding! 🚀**
