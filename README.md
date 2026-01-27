# API Aponta VPS

[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](https://github.com/pedroct/api-aponta-vps)
[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg)](https://conventionalcommits.org)

Backend FastAPI para extensão Azure DevOps, otimizado para deploy em VPS Hostinger com CloudFlare.

## 📋 Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Tecnologias](#tecnologias)
- [Arquitetura](#arquitetura)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Deploy](#deploy)
- [Uso](#uso)
- [Testes](#testes)
- [Contribuindo](#contribuindo)
- [Documentação](#documentação)
- [Licença](#licença)

---

## 🎯 Sobre o Projeto (a ajustar)

API Aponta é um backend robusto desenvolvido em FastAPI para gerenciar atividades e projetos integrados com Azure DevOps. Projetado para alta disponibilidade e segurança em ambiente de produção.

### Características Principais

- ✅ **REST API** completa com documentação Swagger
- ✅ **CRUD** de atividades e projetos
- ✅ **Registro de apontamentos** (horas) com atualização automática no Azure DevOps
- ✅ **Integração** com Azure DevOps
- ✅ **Busca de Work Items** no Azure DevOps
- ✅ **Endpoint de usuário autenticado**
- ✅ **HTTPS/SSL** via CloudFlare Origin Certificate
- ✅ **Docker Compose** para orquestração de containers
- ✅ **Nginx** como proxy reverso com rate limiting
- ✅ **PostgreSQL 15** para persistência de dados
- ✅ **Alembic** para migrations automáticas
- ✅ **Health checks** integrados
- ✅ **CORS** configurável
- ✅ **Conventional Commits** para versionamento semântico
- ✅ **CI/CD** automatizado com GitHub Actions
- ✅ **Testes automatizados** com Pytest e cobertura de código
- ✅ **Global exception handling** com logging estruturado
- ✅ **Deploy automático** via pipeline GitHub Actions

### Informações de Deploy

- **Domínio:** api-aponta.pedroct.com.br
- **VPS:** Hostinger (31.97.16.12)
- **CDN/Proxy:** CloudFlare
- **Ambiente:** Production

---

## 🚀 Tecnologias

### Backend
- **Python 3.12** - Linguagem de programação
- **FastAPI 0.109.0** - Framework web moderno e rápido
- **Uvicorn** - Servidor ASGI de alta performance
- **SQLAlchemy 2.0** - ORM para Python
- **Pydantic** - Validação de dados e settings
- **Alembic** - Migrations de banco de dados

### Banco de Dados
- **PostgreSQL 15 Alpine** - Banco de dados relacional

### Infraestrutura
- **Docker & Docker Compose** - Containerização
- **Nginx Alpine** - Proxy reverso e load balancer
- **CloudFlare** - CDN, DDoS protection e SSL/TLS

### Qualidade de Código
- **Black** - Formatação de código
- **isort** - Ordenação de imports
- **Flake8** - Linting
- **MyPy** - Type checking
- **Pytest** - Framework de testes com coverage

### DevOps & CI/CD
- **GitHub Actions** - Pipeline CI/CD automatizada
- **pytest-cov** - Cobertura de código
- **Codecov** - Relatórios de cobertura
- **Git Flow** - Branching strategy
- **Commitizen** - Conventional Commits e SemVer
- **rsync** - Sincronização de arquivos para VPS

---

## 🏗️ Arquitetura

```
┌─────────────┐
│   Navegador │
└──────┬──────┘
       │ HTTPS (TLS 1.2/1.3)
       ▼
┌─────────────────────┐
│    CloudFlare       │
│  - DDoS Protection  │
│  - SSL/TLS (Full)   │
│  - Rate Limiting    │
└──────┬──────────────┘
       │ HTTPS (Origin Cert)
       ▼
┌─────────────────────┐
│   VPS Hostinger     │
│  ┌───────────────┐  │
│  │ Nginx :80/443 │  │
│  │ - Proxy       │  │
│  │ - Rate Limit  │  │
│  └───────┬───────┘  │
│          │ HTTP     │
│  ┌───────▼───────┐  │
│  │ FastAPI :8000 │  │
│  │ - REST API    │  │
│  │ - Auth        │  │
│  └───────┬───────┘  │
│          │          │
│  ┌───────▼───────┐  │
│  │ PostgreSQL    │  │
│  │ :5432         │  │
│  └───────────────┘  │
└─────────────────────┘
```

### Camadas

1. **CDN/Proxy (CloudFlare)**
   - Proteção DDoS
   - SSL/TLS encryption
   - Cache de conteúdo
   - Rate limiting global

2. **Proxy Reverso (Nginx)**
   - Roteamento de requisições
   - Rate limiting por IP
   - Compressão Gzip
   - Health checks

3. **Aplicação (FastAPI)**
   - Lógica de negócio
   - Validação de dados
   - Autenticação/Autorização
   - Integração com serviços externos

4. **Persistência (PostgreSQL)**
   - Armazenamento de dados
   - Transações ACID
   - Backups automáticos

Para mais detalhes, veja [ARCHITECTURE.md](docs/architecture/ARCHITECTURE.md).

---

## 📦 Instalação

### Pré-requisitos

- **Docker 24+** e **Docker Compose 2.0+**
- **Git**
- **Python 3.12+** (apenas para desenvolvimento local)

### Clone do Repositório

```bash
git clone https://github.com/pedroct/api-aponta-vps.git
cd api-aponta-vps
git checkout develop
```

---

## ⚙️ Configuração

### 1. Variáveis de Ambiente

Copie o arquivo de exemplo e configure:

```bash
cp .env.example .env
nano .env
```

**Variáveis principais:**

```env
# Banco de Dados
DATABASE_NAME=gestao_projetos
DATABASE_USER=api-aponta-user
DATABASE_PASSWORD=<senha-forte>
DATABASE_HOST=postgres
DATABASE_PORT=5432
DATABASE_SCHEMA=api_aponta

# API
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=false
ENVIRONMENT=production

# CORS (sem wildcard)
CORS_ORIGINS=https://api-aponta.pedroct.com.br,https://dev.azure.com,https://vsassets.io,https://sefaz-ceara.gallerycdn.vsassets.io,https://sefaz-ceara-lab.gallerycdn.vsassets.io

# Azure DevOps
AUTH_ENABLED=true
AZURE_DEVOPS_ORG_URL=https://dev.azure.com/sua-org
AZURE_DEVOPS_PAT=<seu-token>
```

### 2. Certificados SSL (Produção)

Para HTTPS com CloudFlare Origin Certificate:

1. Gere o certificado no CloudFlare Dashboard:
   - `SSL/TLS` → `Origin Server` → `Create Certificate`

2. Copie os certificados:
   ```bash
   nano nginx/ssl/fullchain.pem   # Cole o Origin Certificate
   nano nginx/ssl/privkey.pem     # Cole a Private Key
   ```

3. Configure CloudFlare para **Full (strict)** mode

Veja detalhes em: [CLOUDFLARE_SETUP.md](docs/deploy/CLOUDFLARE_SETUP.md)

---

## 🚀 Deploy

### Deploy Automático via CI/CD (Recomendado)

O projeto possui pipeline GitHub Actions que faz deploy automático ao fazer push para `develop` ou `main`:

```bash
git add .
git commit -m "feat: nova funcionalidade"
git push origin develop
```

**Pipeline CI/CD:**
1. 🧪 Executa testes com pytest
2. 📊 Gera relatório de cobertura
3. 🚀 Deploy para VPS (só se testes passarem)
4. ✅ Verifica health check pós-deploy

**Acompanhe:** https://github.com/pedroct/api-aponta-vps/actions

### Deploy Rápido no Servidor

Para deploy manual diretamente no servidor VPS:

```bash
./QUICK_DEPLOY.sh
```

O script irá:
1. ✅ Verificar se `.env` e certificados SSL existem
2. ✅ Parar containers existentes
3. ✅ Construir imagens Docker (sem cache)
4. ✅ Iniciar todos os serviços
5. ✅ Executar migrations do banco
6. ✅ Verificar health da API

### Deploy Manual

```bash
# Build das imagens
docker compose build

# Iniciar serviços
docker compose up -d

# Ver logs
docker compose logs -f

# Verificar status
docker compose ps

# Executar migrations (se necessário)
docker compose exec api alembic upgrade head
```

### Verificação Pós-Deploy

```bash
# Health check
curl https://api-aponta.pedroct.com.br/health

# API Info
curl https://api-aponta.pedroct.com.br/api/v1

# Swagger UI (navegador)
open https://api-aponta.pedroct.com.br/docs
```

Guia completo: [DEPLOY_INSTRUCTIONS.md](docs/deploy/DEPLOY_INSTRUCTIONS.md)

---

## 📖 Uso

### Endpoints Disponíveis

#### Health Check
```bash
GET /health
GET /healthz
GET /
```

#### API Info
```bash
GET /api/v1
```

#### Atividades
```bash
GET    /api/v1/atividades          # Listar todas
GET    /api/v1/atividades/{id}     # Buscar por ID
POST   /api/v1/atividades          # Criar nova
PUT    /api/v1/atividades/{id}     # Atualizar
DELETE /api/v1/atividades/{id}     # Deletar
```

#### Projetos
```bash
GET    /api/v1/projetos            # Listar todos
```

#### Apontamentos
```bash
POST   /api/v1/apontamentos                        # Criar apontamento
GET    /api/v1/apontamentos/work-item/{id}         # Listar por work item
GET    /api/v1/apontamentos/work-item/{id}/resumo  # Resumo por work item
GET    /api/v1/apontamentos/work-item/{id}/azure-info # Info do Azure DevOps
GET    /api/v1/apontamentos/{id}                   # Buscar por ID
PUT    /api/v1/apontamentos/{id}                   # Atualizar
DELETE /api/v1/apontamentos/{id}                   # Excluir
```

#### Integração
```bash
GET    /api/v1/integracao/projetos     # Listar projetos do Azure DevOps
POST   /api/v1/integracao/sincronizar  # Sincronizar projetos localmente
```

#### Work Items
```bash
GET    /api/v1/work-items/search  # Buscar por ID ou título
```

#### Usuário
```bash
GET    /api/v1/user               # Usuário autenticado
```

### Documentação Interativa

- **Swagger UI:** https://api-aponta.pedroct.com.br/docs
- **ReDoc:** https://api-aponta.pedroct.com.br/redoc

Veja exemplos completos em: [API_DOCUMENTATION.md](docs/api/API_DOCUMENTATION.md)

---

## 🧪 Testes

### Executar Testes Localmente

```bash
# Todos os testes
pytest

# Com coverage e relatórios
pytest --cov=app --cov-report=html --cov-report=term

# Testes específicos
pytest tests/test_health.py

# Com verbose
pytest -v

# Sem coverage (mais rápido)
pytest --no-cov
```

### Estrutura de Testes

```
tests/
├── __init__.py              # Package marker
├── conftest.py              # Fixtures compartilhadas (TestClient, DB)
├── test_health.py           # Testes de health check ✅
├── test_atividades.py       # Testes de CRUD de atividades (TODO)
├── test_projetos.py         # Testes de projetos (TODO)
└── test_integration.py      # Testes de integração com Azure (TODO)
```

### CI/CD Testing

Os testes rodam automaticamente no GitHub Actions em cada push:

1. **Test Job**: Executa antes do deploy
2. **PostgreSQL Service**: Banco de teste disponível
3. **Coverage Reports**: Enviados para Codecov
4. **Deploy Condicional**: Só ocorre se testes passarem

**Ver resultados:** https://github.com/pedroct/api-aponta-vps/actions

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor, leia nosso [CONTRIBUTING.md](docs/contributing/CONTRIBUTING.md) para detalhes sobre:

- Código de conduta
- Processo de pull request
- Padrões de código
- Conventional Commits
- Testes requeridos

### Quick Start para Contribuidores

```bash
# 1. Fork o projeto
# 2. Clone seu fork
git clone https://github.com/seu-usuario/api-aponta-vps.git

# 3. Crie uma branch
git checkout -b feature/minha-feature

# 4. Faça suas alterações e commit
git commit -m "feat: adiciona nova funcionalidade"

# 5. Push para o GitHub
git push origin feature/minha-feature

# 6. Abra um Pull Request
```

### Conventional Commits

Usamos [Conventional Commits](https://conventionalcommits.org/) para mensagens de commit:

```
feat: adiciona novo endpoint de relatórios
fix: corrige validação de data
docs: atualiza README com exemplos
chore: atualiza dependências
test: adiciona testes para atividades
```

---

## 📚 Documentação

### Documentação Técnica

- [ARCHITECTURE.md](docs/architecture/ARCHITECTURE.md) - Arquitetura detalhada do sistema
- [API_DOCUMENTATION.md](docs/api/API_DOCUMENTATION.md) - Documentação completa da API
- [CONTRIBUTING.md](docs/contributing/CONTRIBUTING.md) - Guia para contribuidores
- [SECURITY.md](docs/security/SECURITY.md) - Políticas de segurança

### Documentação de Deploy

- [DEPLOY_INSTRUCTIONS.md](docs/deploy/DEPLOY_INSTRUCTIONS.md) - Guia completo de deploy
- [CLOUDFLARE_SETUP.md](docs/deploy/CLOUDFLARE_SETUP.md) - Configuração do CloudFlare
- [CLOUDFLARE_FINAL_SETUP.md](docs/deploy/CLOUDFLARE_FINAL_SETUP.md) - Setup final SSL

### Outros

- [CHANGELOG.md](docs/release/CHANGELOG.md) - Histórico de mudanças
- [WORKSPACE_CONTEXT.md](docs/project/WORKSPACE_CONTEXT.md) - Contexto do projeto

---

## 🔒 Segurança

### Reportar Vulnerabilidades

Por favor, **NÃO** abra issues públicas para vulnerabilidades de segurança.

Envie um email para: **security@pedroct.com.br**

Veja: [SECURITY.md](docs/security/SECURITY.md)

### Boas Práticas Implementadas

- ✅ HTTPS obrigatório (CloudFlare + Origin Certificate)
- ✅ Rate limiting em múltiplas camadas
- ✅ CORS configurável
- ✅ Secrets em variáveis de ambiente (não versionadas)
- ✅ Usuário não-root nos containers
- ✅ Health checks para todos os serviços
- ✅ Logs estruturados

---

## 📊 Status do Projeto

### Roadmap

#### v0.1.0 (Atual) ✅
- [x] Setup inicial do projeto
- [x] Configuração Docker Compose
- [x] Nginx proxy reverso
- [x] SSL/TLS com CloudFlare
- [x] Endpoints básicos de atividades
- [x] Integração Azure DevOps
- [x] Documentação inicial
- [x] Pipeline CI/CD com GitHub Actions
- [x] Testes automatizados com Pytest
- [x] Coverage reports com Codecov
- [x] Global exception handler
- [x] Logging estruturado
- [x] Deploy automático via pipeline

#### v0.2.0 (Próximo)
- [ ] Testes de integração completos
- [ ] Monitoramento e logs centralizados
- [ ] Backup automático do banco
- [ ] Métricas e observabilidade
- [ ] Cache de respostas
- [ ] Documentação de API melhorada

#### v1.0.0 (Futuro)
- [ ] Autenticação JWT
- [ ] Websockets para notificações
- [ ] Cache com Redis
- [ ] API versioning
- [ ] Rate limiting por usuário

---

## 🛠️ Comandos Úteis

### Docker

```bash
# Logs de todos os serviços
docker compose logs -f

# Logs de um serviço específico
docker compose logs -f api

# Reiniciar serviços
docker compose restart

# Parar tudo
docker compose down

# Rebuild e restart
docker compose up -d --build

# Entrar no container da API
docker exec -it api-aponta bash

# Ver uso de recursos
docker stats
```

### Banco de Dados

```bash
# Entrar no PostgreSQL
docker exec -it postgres-aponta psql -U api-aponta-user -d gestao_projetos

# Backup do banco
docker exec postgres-aponta pg_dump -U api-aponta-user gestao_projetos > backup.sql

# Restore do banco
docker exec -i postgres-aponta psql -U api-aponta-user gestao_projetos < backup.sql

# Ver migrations
docker exec api-aponta alembic history

# Executar migrations
docker exec api-aponta alembic upgrade head
```

### Git

```bash
# Commit com Commitizen
cz commit

# Bump de versão
cz bump --changelog

# Ver histórico
git log --oneline --graph

# Sincronizar com remoto
git pull --rebase origin develop
```

---

## 👥 Equipe

- **Desenvolvedor Principal:** Pedro CT
- **Repositório:** [github.com/pedroct/api-aponta-vps](https://github.com/pedroct/api-aponta-vps)

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 🙏 Agradecimentos

- [FastAPI](https://fastapi.tiangolo.com/) - Framework web incrível
- [CloudFlare](https://www.cloudflare.com/) - CDN e segurança
- [Hostinger](https://www.hostinger.com.br/) - Hosting VPS
- [Azure DevOps](https://dev.azure.com/) - Integração principal

---

## 📞 Suporte

- **Issues:** [GitHub Issues](https://github.com/pedroct/api-aponta-vps/issues)
- **Discussões:** [GitHub Discussions](https://github.com/pedroct/api-aponta-vps/discussions)
- **Email:** contato@pedroct.com.br

---

<p align="center">
  Feito com ❤️ por <a href="https://github.com/pedroct">Pedro CT</a>
</p>

<p align="center">
  <sub>Built with Python 🐍 | Powered by FastAPI ⚡ | Secured by CloudFlare 🛡️</sub>
</p>
