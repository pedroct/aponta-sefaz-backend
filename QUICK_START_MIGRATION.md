# 🚀 Quick Start: Migração Project ID

## Para Desenvolvedores

### 1️⃣ Validar Localmente (ANTES da migração)

```bash
cd /home/pedroctdev/apps/api-aponta-vps

# Executar script de validação
python validar_migracao.py
```

Este script verifica:
- ✅ Projetos disponíveis no banco
- ✅ Quantos registros precisam ser migrados
- ✅ Simulação da migração (sem modificar dados)

### 2️⃣ Executar Migração Local

```bash
# Executar migração Alembic
alembic upgrade head

# Validar novamente
python validar_migracao.py
```

### 3️⃣ Testar Endpoints

```bash
# Iniciar servidor local
uvicorn app.main:app --reload

# Em outro terminal, testar:
# 1. Criar apontamento com UUID
curl -X POST "http://localhost:8000/api/v1/apontamentos" \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "work_item_id": 123,
    "project_id": "50a9ca09-710f-4478-8278-2d069902d2af",
    "organization_name": "sefaz-rs",
    "data_apontamento": "2026-01-25",
    "duracao": "02:00",
    "id_atividade": "uuid-da-atividade",
    "usuario_id": "user-123",
    "usuario_nome": "Pedro",
    "usuario_email": "pedro@example.com"
  }'

# 2. Buscar timesheet
curl "http://localhost:8000/api/v1/timesheet?organization_name=sefaz-rs&project_id=50a9ca09-710f-4478-8278-2d069902d2af" \
  -H "Authorization: Bearer SEU_TOKEN"
```

### 4️⃣ Deploy para Staging

```bash
# Commit e push
git add .
git commit -m "feat: normalizar project_id para UUID"
git push origin develop

# GitHub Actions fará o deploy automático
# Aguarde o workflow completar em: https://github.com/pedroct/aponta-sefaz-backend/actions
```

### 5️⃣ Executar Migração em Staging

```bash
# Conectar via SSH
ssh -i C:\Users\pedro\.ssh\hostinger_github_deploy_key root@92.112.178.252

# Navegar para staging
cd /home/ubuntu/aponta-sefaz/staging/backend

# Executar migração
docker-compose exec backend alembic upgrade head

# Ver logs
docker-compose logs backend | tail -100

# Validar (opcional)
docker-compose exec backend python validar_migracao.py
```

### 6️⃣ Monitorar Logs

```bash
# Ver logs em tempo real
docker-compose logs backend -f

# Filtrar por project_id
docker-compose logs backend | grep -i "project_id\|normalizado"

# Verificar erros
docker-compose logs backend | grep -i "error\|exception"
```

## 🆘 Troubleshooting

### Problema: "Projeto não encontrado"

```sql
-- Conectar no banco
docker-compose exec db psql -U postgres -d aponta_sefaz

-- Ver projetos existentes
SELECT nome, external_id FROM projetos;

-- Adicionar projeto se necessário
INSERT INTO projetos (id, external_id, nome, descricao)
VALUES (gen_random_uuid(), '50a9ca09-710f-4478-8278-2d069902d2af', 'DEV', 'Desenvolvimento');
```

### Rollback da Migração

```bash
# Reverter última migração
docker-compose exec backend alembic downgrade -1

# Ver histórico
docker-compose exec backend alembic history
```

### Verificar Dados

```sql
-- Contar por formato
SELECT 
  CASE 
    WHEN project_id LIKE '%-%' THEN 'UUID'
    ELSE 'NOME'
  END as formato,
  COUNT(*) as total
FROM apontamentos
GROUP BY formato;

-- Ver project_id distintos
SELECT DISTINCT project_id FROM apontamentos;

-- Ver registros antigos
SELECT * FROM apontamentos 
WHERE project_id NOT LIKE '%-%' 
LIMIT 10;
```

## 📚 Documentação Completa

- **Guia Detalhado**: [docs/migration/PROJECT_ID_TO_UUID_MIGRATION.md](docs/migration/PROJECT_ID_TO_UUID_MIGRATION.md)
- **Resumo**: [MIGRATION_SUMMARY.md](MIGRATION_SUMMARY.md)
- **Código do Script**: [alembic/versions/e5f6g7h8i9j0_migrate_project_id_to_uuid.py](alembic/versions/e5f6g7h8i9j0_migrate_project_id_to_uuid.py)

## 🔗 Links Úteis

- **Repositório**: https://github.com/pedroct/aponta-sefaz-backend
- **Staging Workflow**: .github/workflows/deploy-staging.yml
- **Production Workflow**: .github/workflows/deploy-production.yml
- **VPS**: root@92.112.178.252

## ✅ Checklist

- [ ] Validar localmente com `python validar_migracao.py`
- [ ] Executar `alembic upgrade head` localmente
- [ ] Testar criação de apontamento localmente
- [ ] Commit e push para `develop`
- [ ] Aguardar deploy staging
- [ ] Executar migração em staging
- [ ] Testar em staging
- [ ] Deploy para produção
- [ ] Executar migração em produção
- [ ] Monitorar logs por 24h
