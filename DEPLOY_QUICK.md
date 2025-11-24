# 🚀 Deploy Rápido - 5 Minutos

## ⚡ **OPÇÃO MAIS FÁCIL: RAILWAY** (Recomendado)

### 📋 Pré-requisitos
- Conta no GitHub (já tem ✅)
- 5 minutos

### 🎯 Passo a Passo (literalmente 3 cliques)

#### 1️⃣ Criar Conta no Railway
```
👉 Acesse: https://railway.app/
👉 Click "Login with GitHub"
👉 Autorize o Railway
```

#### 2️⃣ Criar Projeto do GitHub
```
1. No Railway, click "New Project"
2. Selecione "Deploy from GitHub repo"
3. Procure e selecione: "e0a47847-faculdade-career-matching"
4. Railway detecta Docker automaticamente ✅
5. Click "Deploy Now"
```

#### 3️⃣ Adicionar PostgreSQL
```
1. No projeto criado, click "+ New"
2. Selecione "Database"
3. Escolha "PostgreSQL"
4. Pronto! Database criado automaticamente ✅
```

#### 4️⃣ Conectar Database ao App
```
1. Click no serviço "faculdade-career-matching"
2. Vá em "Variables"
3. Click "+ New Variable"
4. Adicione:
   
   Nome: DATABASE_URL
   Valor: ${{Postgres.DATABASE_URL}}
   
5. Click "Add"
```

#### 5️⃣ Aguardar Deploy
```
✅ Build inicia automaticamente
✅ Aguarde ~3 minutos
✅ Status mudará para "Active"
```

#### 6️⃣ Acessar sua API
```
1. Click no serviço
2. Vá em "Settings"
3. Copie a URL em "Domains"
4. Cole no browser + /docs

Exemplo: https://faculdade-career-matching-production.up.railway.app/docs
```

---

## 🎉 **PRONTO! Sua API está no ar!**

### Teste agora:

```bash
# Health check
curl https://sua-url.railway.app/health

# Ver documentação
https://sua-url.railway.app/docs

# API Info
curl https://sua-url.railway.app/api/v1/info
```

---

## 📊 **Carregar Dados de Exemplo**

### Opção 1: Via Railway CLI

```bash
# Instalar CLI
npm install -g @railway/cli

# Login
railway login

# Link ao projeto
railway link

# Executar seed
railway run python -m src.utils.seed_data
```

### Opção 2: Criar endpoint de seed (recomendado)

Adicione ao código:

```python
@app.post("/api/v1/seed")
async def seed_database(db: Session = Depends(get_db)):
    from src.utils.seed_data import seed_all
    seed_all()
    return {"message": "Database seeded successfully"}
```

Depois chame:
```bash
curl -X POST https://sua-url.railway.app/api/v1/seed
```

---

## 🔧 **Configurações Adicionais (Opcional)**

### Domínio Customizado

```
1. Railway → Settings → Domains
2. Click "Add Custom Domain"
3. Digite: api.seusite.com
4. Configure DNS conforme instruções
```

### Variáveis de Ambiente Extras

```
Railway → Variables → Add:

- SECRET_KEY=your-secret-key
- REDIS_URL=redis://...
- ALLOWED_ORIGINS=https://seusite.com
```

### Auto-Deploy do GitHub

```
✅ Já configurado!
Cada push no GitHub = deploy automático
```

---

## 💰 **Custos**

### Railway Pricing:
- **$5 de crédito grátis** todo mês
- Depois do crédito: **$5-20/mês** (baseado em uso)
- PostgreSQL incluído no preço

### Uso Estimado:
```
API (512MB RAM): ~$5/mês
PostgreSQL: Incluído
Total: ~$5/mês (ou grátis se ficar dentro do crédito)
```

---

## 📞 **Suporte**

### Problemas?

1. **Logs em tempo real:**
   ```
   Railway → Seu Projeto → View Logs
   ```

2. **Discord do Railway:**
   ```
   https://discord.gg/railway
   ```

3. **Documentação:**
   ```
   https://docs.railway.app/
   ```

---

## ✅ **Checklist Final**

- [ ] Conta criada no Railway
- [ ] Projeto criado do GitHub
- [ ] PostgreSQL adicionado
- [ ] DATABASE_URL configurado
- [ ] Deploy completado (status "Active")
- [ ] API testada (https://sua-url.railway.app/docs)
- [ ] Dados de exemplo carregados (opcional)

---

## 🎯 **Próximos Passos**

1. ✅ **Deploy feito!** Sua API está online
2. 📱 **Teste todos os endpoints** no /docs
3. 🔗 **Integre com frontend** (se tiver)
4. 📊 **Configure monitoramento**
5. 🚀 **Compartilhe com o mundo!**

---

## 🌟 **Alternativas ao Railway**

Se preferir outra plataforma, veja o arquivo `DEPLOY.md` para:
- **Render.com** (gratuito forever)
- **Fly.io** (deploy global)
- **Digital Ocean** (produção enterprise)

---

**🚀 Comece agora: https://railway.app/**

**Tempo total: 5 minutos ⏱️**

---

## 📸 **Screenshots do Processo**

### 1. Railway Dashboard
```
[New Project] → Deploy from GitHub repo
```

### 2. Selecionar Repositório
```
🔍 Search: e0a47847-faculdade-career-matching
✅ Select
```

### 3. Deploy Status
```
🔨 Building...
✅ Deployed
🌐 URL: https://...railway.app
```

---

## 🎊 **Parabéns!**

Sua API FastAPI está rodando em produção! 🎉

Agora você pode:
- ✅ Acessar de qualquer lugar
- ✅ Compartilhar com clientes
- ✅ Integrar com aplicações
- ✅ Escalar conforme necessário

**Happy Deploying! 🚀**
