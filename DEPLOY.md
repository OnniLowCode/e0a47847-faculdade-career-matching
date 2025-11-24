# 🚀 Guia de Deploy - Faculty Career Matching System

## ⚠️ Importante: Vercel e FastAPI

O **Vercel não suporta FastAPI** nativamente. Vercel é otimizado para:
- Next.js
- Node.js
- Frontend estático

Para FastAPI, você precisa de uma plataforma que suporte Python e long-running processes.

---

## ✅ **OPÇÃO 1: RAILWAY** (⭐ RECOMENDADO - Mais Fácil)

### Por que Railway?
- ✅ Deploy automático do GitHub
- ✅ PostgreSQL incluído gratuitamente
- ✅ SSL automático
- ✅ $5/mês de crédito gratuito
- ✅ Interface super simples

### Passo a Passo:

#### 1. Criar conta no Railway
```
https://railway.app/
```
- Login com GitHub
- Autorize o acesso ao repositório

#### 2. Criar novo projeto
```
1. Click "New Project"
2. Selecione "Deploy from GitHub repo"
3. Escolha: e0a47847-faculdade-career-matching
4. Railway detecta automaticamente Python/Docker
```

#### 3. Adicionar PostgreSQL
```
1. No seu projeto, click "+ New"
2. Selecione "Database"
3. Escolha "PostgreSQL"
4. Railway cria automaticamente
```

#### 4. Configurar Variáveis de Ambiente
```
No painel do serviço FastAPI, vá em "Variables":

DATABASE_URL = ${{Postgres.DATABASE_URL}}
PORT = 8000
PYTHON_VERSION = 3.11
```

#### 5. Deploy Automático!
```
✅ Railway faz build do Docker automaticamente
✅ Deploy completa em ~3 minutos
✅ URL gerada: https://faculdade-career-matching-production.up.railway.app
```

#### 6. Acessar a API
```
https://seu-projeto.up.railway.app/docs
```

### Comandos Úteis (Railway CLI - opcional)

```bash
# Instalar CLI
npm i -g @railway/cli

# Login
railway login

# Ver logs
railway logs

# Abrir no browser
railway open
```

**Custo:** Gratuito ($5 crédito/mês) ou $5-20/mês depois

---

## ✅ **OPÇÃO 2: RENDER.COM** (Gratuito Forever)

### Por que Render?
- ✅ Tier gratuito permanente
- ✅ PostgreSQL incluído
- ✅ SSL automático
- ✅ Deploy do GitHub
- ⚠️ Adormece após inatividade (tier free)

### Passo a Passo:

#### 1. Criar conta no Render
```
https://render.com/
```

#### 2. Criar Web Service
```
1. Dashboard → "New" → "Web Service"
2. Connect GitHub
3. Selecionar repositório: e0a47847-faculdade-career-matching
```

#### 3. Configurar o Serviço
```yaml
Name: faculty-career-matching
Environment: Docker
Region: Oregon (ou Frankfurt para EU)
Branch: main
Docker Command: (deixar vazio - usa CMD do Dockerfile)
Instance Type: Free
```

#### 4. Adicionar PostgreSQL
```
1. Dashboard → "New" → "PostgreSQL"
2. Name: faculty-db
3. Database: faculty_career
4. User: faculty_user
5. Region: Same as web service
6. Plan: Free
```

#### 5. Variáveis de Ambiente
```
No Web Service, aba "Environment":

DATABASE_URL = (copiar do PostgreSQL criado)
# Formato: postgresql://user:password@host/dbname

PORT = 8000
PYTHON_VERSION = 3.11
```

#### 6. Deploy
```
Click "Manual Deploy" → "Deploy latest commit"
Ou ative "Auto-Deploy" para deploy automático em cada push
```

#### 7. Acessar
```
https://faculty-career-matching.onrender.com/docs
```

**Custo:** Gratuito (com sleep após inatividade) ou $7/mês (sempre ativo)

---

## ✅ **OPÇÃO 3: FLY.IO** (Deploy Global)

### Por que Fly.io?
- ✅ Deploy em múltiplas regiões
- ✅ PostgreSQL incluído
- ✅ Configuração via arquivo
- ✅ CLI poderosa

### Passo a Passo:

#### 1. Instalar Fly CLI

```bash
# macOS/Linux
curl -L https://fly.io/install.sh | sh

# Windows (PowerShell)
iwr https://fly.io/install.ps1 -useb | iex
```

#### 2. Login
```bash
fly auth login
```

#### 3. Criar fly.toml (já está no projeto!)

O arquivo `fly.toml` já foi criado:

```toml
app = "faculty-career-matching"
primary_region = "gru"  # São Paulo

[build]

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 0

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 512
```

#### 4. Launch (na pasta do projeto)

```bash
cd /caminho/para/faculdade_career_matching
fly launch --no-deploy
```

Responda:
```
? Choose an app name: faculty-career-matching
? Choose a region: gru (São Paulo)
? Would you like to set up a PostgreSQL database? Yes
? Select configuration: Development - Single node, 1x shared CPU, 256MB RAM, 1GB disk
? Would you like to deploy now? No
```

#### 5. Configurar Secrets

```bash
# Fly cria DATABASE_URL automaticamente
# Adicionar outros secrets se necessário
fly secrets set SECRET_KEY=your-secret-key-here
```

#### 6. Deploy

```bash
fly deploy
```

#### 7. Acessar

```bash
fly open
# Ou acesse: https://faculty-career-matching.fly.dev/docs
```

#### 8. Ver Logs

```bash
fly logs
```

**Custo:** ~$5-10/mês

---

## ✅ **OPÇÃO 4: DIGITAL OCEAN APP PLATFORM**

### Passo a Passo Rápido:

```
1. https://cloud.digitalocean.com/apps
2. "Create App" → GitHub
3. Selecionar repositório
4. Detect Dockerfile automaticamente
5. Adicionar PostgreSQL Managed Database
6. Deploy!
```

**Custo:** $5/mês (app) + $15/mês (database)

---

## 📊 **COMPARAÇÃO RÁPIDA**

| Plataforma | Gratuito | Fácil | PostgreSQL | SSL | Recomendação |
|------------|----------|-------|------------|-----|--------------|
| **Railway** | $5 crédito | ⭐⭐⭐⭐⭐ | ✅ Grátis | ✅ Auto | **Melhor geral** |
| **Render** | ✅ Sim* | ⭐⭐⭐⭐ | ✅ Grátis | ✅ Auto | **Melhor grátis** |
| **Fly.io** | Generoso | ⭐⭐⭐ | ✅ Incluído | ✅ Auto | **Melhor global** |
| **DigitalOcean** | ❌ Não | ⭐⭐⭐⭐ | $15/mês | ✅ Auto | Produção |

*Render free tier hiberna após 15min de inatividade

---

## 🎯 **RECOMENDAÇÃO FINAL**

### Para você, recomendo **RAILWAY**:

**Por quê?**
1. ✅ Mais fácil e rápido (5 minutos)
2. ✅ Detecção automática de Docker
3. ✅ PostgreSQL grátis
4. ✅ $5 de crédito inicial
5. ✅ Interface intuitiva
6. ✅ Deploy automático do GitHub

### **Deploy AGORA em Railway (3 passos):**

```bash
1. Acesse: https://railway.app/
2. "New Project" → "Deploy from GitHub repo"
3. Selecione: e0a47847-faculdade-career-matching
4. Aguarde 3 minutos
5. Pronto! ✅
```

---

## 🔧 **Após o Deploy**

### 1. Testar a API

```bash
# Substituir pela sua URL
curl https://seu-app.railway.app/health

# Ver docs
https://seu-app.railway.app/docs
```

### 2. Carregar Dados de Exemplo

```bash
# Via Railway CLI
railway run python -m src.utils.seed_data

# Ou via endpoint (se criar um)
curl -X POST https://seu-app.railway.app/api/v1/seed
```

### 3. Monitoramento

**Railway:**
- Dashboard → Metrics
- Logs em tempo real

**Render:**
- Dashboard → Logs
- Metrics tab

**Fly.io:**
```bash
fly logs
fly status
fly scale show
```

---

## 🚨 **Troubleshooting**

### Erro: "Database connection failed"

```bash
# Verificar DATABASE_URL
echo $DATABASE_URL

# Railway
railway variables

# Render
# Ver em Settings → Environment
```

### Erro: "Port already in use"

Certifique-se que a variável `PORT` está configurada:
```
PORT=8000
```

### App não inicia

```bash
# Ver logs
railway logs  # Railway
# ou
# Render dashboard → Logs
```

---

## 📞 **Precisa de Ajuda?**

**Documentação:**
- Railway: https://docs.railway.app/
- Render: https://render.com/docs
- Fly.io: https://fly.io/docs

**Suporte:**
- Railway Discord: https://discord.gg/railway
- Render Community: https://community.render.com/

---

## ✅ **PRÓXIMOS PASSOS**

1. ✅ Escolha uma plataforma (recomendo Railway)
2. ✅ Faça o deploy seguindo o guia acima
3. ✅ Teste a API
4. ✅ Configure domínio customizado (opcional)
5. ✅ Configure CI/CD para deploy automático

---

## 🎉 **BÔNUS: Domínio Customizado**

Depois do deploy, você pode adicionar um domínio:

### Railway:
```
Settings → Domains → Add Custom Domain
```

### Render:
```
Settings → Custom Domains → Add
```

### Fly.io:
```bash
fly certs add seudominio.com
```

---

**🚀 Pronto para fazer deploy? Escolha Railway e siga os 3 passos acima!**

Qualquer dúvida, me avise! 😊
