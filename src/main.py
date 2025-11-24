from fastapi import FastAPI

app = FastAPI(title="faculdade_career_matching", description="Sistema FastAPI que conecta notas da grade curricular com empresas parceiras que buscam candidatos com perfis acadêmicos específicos")

@app.get("/")
async def root():
    return {"message": "Welcome to faculdade_career_matching"}

@app.get("/health")
async def health():
    return {"status": "healthy"}