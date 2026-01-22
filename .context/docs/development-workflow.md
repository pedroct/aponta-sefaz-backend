---
type: doc
name: development-workflow
description: Day-to-day engineering processes, branching, and contribution guidelines
category: workflow
generated: 2026-01-22
status: filled
scaffoldVersion: "2.0.0"
---
## Development Workflow

Fluxo de desenvolvimento do Sistema Aponta com CI/CD automatizado.

## Branching & Releases

| Branch | Purpose | Deploy |
|--------|---------|--------|
| `develop` | Development branch | Auto-deploy para Staging |
| `main` | Production branch | Auto-deploy para Produção |

### Commit Convention

Seguir [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(scope): add new feature
fix(scope): fix bug
docs(scope): update documentation
refactor(scope): code refactoring
test(scope): add tests
chore(scope): maintenance tasks
```

Exemplos:
- `feat(auth): implementar validação de App Token JWT`
- `fix(azure): usar PAT do backend para chamadas API`
- `docs(deploy): atualizar guia de deploy`

## Local Development

### Prerequisites
- Python 3.12+
- PostgreSQL 15+
- Docker (opcional)

### Setup

```bash
# Clone e entre no diretório
git clone https://github.com/pedroct/aponta-sefaz-backend.git
cd aponta-sefaz-backend

# Crie e ative virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Instale dependências
pip install -r requirements.txt

# Configure variáveis de ambiente
cp .env.example .env
# Edite .env com suas configurações

# Execute migrações
alembic upgrade head

# Inicie o servidor
uvicorn app.main:app --reload
```

### Commands

| Command | Description |
|---------|-------------|
| `uvicorn app.main:app --reload` | Run development server |
| `alembic upgrade head` | Run migrations |
| `alembic revision -m "message"` | Create new migration |
| `pytest tests/ -v` | Run tests |
| `pytest tests/ --watch` | Run tests in watch mode |

## CI/CD Pipeline

### GitHub Actions Workflows

| Workflow | Trigger | Action |
|----------|---------|--------|
| `deploy-staging.yml` | Push to `develop` | Test + Deploy to Staging |
| `deploy-production.yml` | Push to `main` | Test + Deploy to Production |

### Pipeline Steps

1. **Test**: Run pytest suite
2. **Deploy**: rsync to VPS + docker compose rebuild
3. **Verify**: Health check on deployed container

## Deploy Manual (Hotfix)

Para correções urgentes sem passar pelo CI/CD:

```bash
# 1. Copiar arquivo para VPS
scp app/services/azure.py root@92.112.178.252:/tmp/

# 2. Copiar para dentro do container
ssh root@92.112.178.252 "docker cp /tmp/azure.py api-aponta-staging:/app/app/services/azure.py"

# 3. Reiniciar container
ssh root@92.112.178.252 "docker restart api-aponta-staging"
```

⚠️ **Importante**: Sempre commitar e fazer push após um hotfix manual!

## Code Review Expectations

- [ ] Testes passando localmente
- [ ] Sem secrets hardcoded
- [ ] Migrações compatíveis com rollback
- [ ] Documentação atualizada (se necessário)
- [ ] Conventional Commits no título do PR

## Useful Commands

```bash
# Ver logs do container staging
ssh root@92.112.178.252 "docker logs api-aponta-staging --tail 50"

# Verificar status dos containers
ssh root@92.112.178.252 "docker ps --format 'table {{.Names}}\t{{.Status}}'"

# Verificar variáveis no container
ssh root@92.112.178.252 "docker exec api-aponta-staging printenv | grep AZURE"

# Testar health endpoint
curl https://staging-aponta.treit.com.br/health
```

## Related Resources

- [testing-strategy.md](./testing-strategy.md)
- [tooling.md](./tooling.md)
- [architecture.md](./architecture.md)
