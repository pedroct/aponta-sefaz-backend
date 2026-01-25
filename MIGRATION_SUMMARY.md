# Resumo: Normalização de project_id para UUID

## 📋 Mudanças Implementadas

### 1. ✅ Script de Migração Alembic
**Arquivo**: [`alembic/versions/e5f6g7h8i9j0_migrate_project_id_to_uuid.py`](../alembic/versions/e5f6g7h8i9j0_migrate_project_id_to_uuid.py)

- Converte `project_id` de nome ("DEV") para UUID automaticamente
- Busca correspondência na tabela `projetos`
- Fornece relatório detalhado da migração
- Suporta rollback (downgrade)

### 2. ✅ Helper de Normalização
**Arquivo**: [`app/utils/project_id_normalizer.py`](../app/utils/project_id_normalizer.py)

Três funções principais:
- `is_valid_uuid(value)` - Verifica se é UUID válido
- `normalize_project_id(project_id, db)` - Converte nome → UUID
- `validate_project_id_format(project_id)` - Valida formato

### 3. ✅ Validação no Schema
**Arquivo**: [`app/schemas/apontamento.py`](../app/schemas/apontamento.py)

- Validador `@field_validator("project_id")` adicionado
- Aceita UUID (recomendado) ou nome (transição)
- Mensagens de erro claras

### 4. ✅ Atualização dos Serviços

#### [`app/services/apontamento_service.py`](../app/services/apontamento_service.py)
- Normaliza `project_id` ao criar apontamento
- Fallback gracioso se normalização falhar

#### [`app/services/timesheet_service.py`](../app/services/timesheet_service.py)
- Query usa `or_()` para aceitar ambos os formatos
- Logs informativos sobre normalização

### 5. ✅ Testes
**Arquivo**: [`tests/test_project_id_normalizer.py`](../tests/test_project_id_normalizer.py)

- Testes de validação de UUID
- Testes de normalização
- Fixtures para projetos mock

### 6. ✅ Documentação
**Arquivo**: [`docs/migration/PROJECT_ID_TO_UUID_MIGRATION.md`](../docs/migration/PROJECT_ID_TO_UUID_MIGRATION.md)

Guia completo com:
- Contexto e problema
- Solução implementada
- Plano de deploy (staging → produção)
- Comandos úteis
- Troubleshooting

## 🎯 O Que Foi Resolvido

### Problema Original
```
# Registros antigos (Gestão de Apontamentos)
project_id: "DEV"

# Registros novos (Modal do Work Item)  
project_id: "50a9ca09-710f-4478-8278-2d069902d2af"
```

### Solução
1. ✅ **Migração de dados**: Converte registros antigos automaticamente
2. ✅ **Validação**: Garante que novos registros usem UUID
3. ✅ **Compatibilidade**: Aceita ambos os formatos durante transição
4. ✅ **Queries**: Filtra corretamente independente do formato

## 🚀 Próximos Passos

### Fase 1: Testes Locais
```bash
cd /home/pedroctdev/apps/api-aponta-vps

# Executar migração
alembic upgrade head

# Verificar registros
python -c "
from app.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
result = db.execute(text('''
    SELECT 
        CASE 
            WHEN project_id LIKE '%-%' THEN 'UUID'
            ELSE 'NOME'
        END as formato,
        COUNT(*) as total
    FROM apontamentos
    GROUP BY formato
'''))
for row in result:
    print(f'{row[0]}: {row[1]} registros')
db.close()
"

# Executar testes
pytest tests/test_project_id_normalizer.py -v
```

### Fase 2: Deploy Staging
```bash
# Commit e push
git add .
git commit -m "feat: normalizar project_id para UUID em apontamentos

- Adiciona script Alembic para migração de dados
- Implementa helper de normalização project_id
- Adiciona validação UUID no schema
- Atualiza serviços para aceitar ambos os formatos
- Adiciona documentação completa de migração"

git push origin develop

# Aguardar deploy automático do GitHub Actions

# Conectar na VPS e executar migração
ssh -i C:\Users\pedro\.ssh\hostinger_github_deploy_key root@92.112.178.252
cd /home/ubuntu/aponta-sefaz/staging/backend
docker-compose exec backend alembic upgrade head
docker-compose logs backend | tail -50
```

### Fase 3: Validação em Staging
- [ ] Testar criação de apontamento pela tela Gestão
- [ ] Testar criação de apontamento pelo Modal do Work Item
- [ ] Verificar endpoint `/api/v1/timesheet`
- [ ] Confirmar que ambos os formatos funcionam
- [ ] Verificar logs sem erros

### Fase 4: Deploy Produção
```bash
# Após validação em staging
git checkout main
git merge develop
git push origin main

# Aguardar deploy automático

# Conectar na VPS e executar migração
ssh -i C:\Users\pedro\.ssh\hostinger_github_deploy_key root@92.112.178.252
cd /home/ubuntu/aponta-sefaz/production/backend
docker-compose exec backend alembic upgrade head
docker-compose logs backend -f
```

## 📊 Arquivos Criados/Modificados

### Criados
- ✅ `alembic/versions/e5f6g7h8i9j0_migrate_project_id_to_uuid.py`
- ✅ `app/utils/__init__.py`
- ✅ `app/utils/project_id_normalizer.py`
- ✅ `tests/test_project_id_normalizer.py`
- ✅ `docs/migration/PROJECT_ID_TO_UUID_MIGRATION.md`

### Modificados
- ✅ `app/schemas/apontamento.py`
- ✅ `app/services/apontamento_service.py`
- ✅ `app/services/timesheet_service.py`

## 🔍 Comandos de Verificação

### Verificar registros não migrados
```sql
docker-compose exec db psql -U postgres -d aponta_sefaz -c "
SELECT DISTINCT project_id 
FROM apontamentos 
WHERE project_id NOT LIKE '%-%' 
  AND LENGTH(project_id) < 36;
"
```

### Contar por formato
```sql
docker-compose exec db psql -U postgres -d aponta_sefaz -c "
SELECT 
  CASE 
    WHEN project_id LIKE '%-%' THEN 'UUID'
    ELSE 'NOME'
  END as formato,
  COUNT(*) as total
FROM apontamentos
GROUP BY formato;
"
```

### Verificar logs de normalização
```bash
docker-compose logs backend | grep -i "project_id\|normalizado"
```

## ⚠️ Atenção

### Durante a Transição
- Backend aceita **ambos** os formatos (UUID e nome)
- Recomendado enviar sempre UUID do frontend
- Queries usam `OR` para compatibilidade

### Após Estabilização
Remover suporte ao formato antigo:
1. Atualizar `TimesheetService._get_apontamentos_semana()` para filtrar apenas por UUID
2. Tornar validação UUID obrigatória no schema
3. Remover lógica de fallback

## 📚 Documentação Adicional

- **Guia completo**: [PROJECT_ID_TO_UUID_MIGRATION.md](../docs/migration/PROJECT_ID_TO_UUID_MIGRATION.md)
- **Repositório**: https://github.com/pedroct/aponta-sefaz-backend
- **Workflows**: `.github/workflows/deploy-staging.yml` e `.github/workflows/deploy-production.yml`
