# faculdade_career_matching

Sistema FastAPI que conecta notas da grade curricular com empresas parceiras que buscam candidatos com perfis acadêmicos específicos

## Setup

```bash
pip install -r requirements.txt
uvicorn src.main:app --reload
```

## Docker

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```
