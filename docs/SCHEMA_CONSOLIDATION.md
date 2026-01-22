# Schema Consolidation - Database Cleanup

## Overview

**Objetivo**: Consolidar os schemas de banco de dados, removendo completamente:
- ❌ `api_aponta` (schema antigo de produção)
- ❌ `api_aponta_staging` (schema antigo de staging)  
- ❌ Qualquer dado em `public` (schema padrão PostgreSQL)

**Resultado final**:
- ✅ **Produção**: `aponta_sefaz`
- ✅ **Staging**: `aponta_sefaz_staging`
- ✅ **Nada em**: `public`, `api_aponta`, `api_aponta_staging`

---

## Configurações Aplicadas

### 1. Environment Variables

**`.env` (Produção)**:
```bash
DATABASE_SCHEMA=aponta_sefaz
```

**`.env.staging` (Staging)**:
```bash
DATABASE_SCHEMA=aponta_sefaz_staging
```

**`.env.example` (Template)**:
```bash
DATABASE_SCHEMA=aponta_sefaz  # Padrão para produção
```

### 2. Application Configuration

**`app/config.py`**:
```python
database_schema: str = Field(
    "aponta_sefaz",  # Padrão para produção (alterado de "public")
    validation_alias=AliasChoices("DATABASE_SCHEMA", "database_schema")
)
```

### 3. Database Initialization

**`scripts/init-schema.sql`**:
```sql
-- Criar schemas corretos
CREATE SCHEMA IF NOT EXISTS aponta_sefaz;
CREATE SCHEMA IF NOT EXISTS aponta_sefaz_staging;

-- Remover schemas antigos
DROP SCHEMA IF EXISTS api_aponta CASCADE;
DROP SCHEMA IF EXISTS api_aponta_staging CASCADE;

-- Search path padrão
ALTER DATABASE gestao_projetos SET search_path TO aponta_sefaz;
```

### 4. Docker Compose

**`docker-compose.yml` (Produção)**:
```yaml
environment:
  - DATABASE_SCHEMA=aponta_sefaz
```

**`docker-compose.staging.yml` (Staging)**:
```yaml
environment:
  - DATABASE_SCHEMA=aponta_sefaz_staging
```

---

## Cleanup Procedure

### Option 1: Automatic via Alembic (Recommended)

A migration `cleanup_old_1234567890` foi adicionada para:
1. Remover schemas `api_aponta` e `api_aponta_staging`
2. Limpar tabelas do schema `public`
3. Remover sequências do schema `public`

**Execute**:
```bash
# Produção
cd /path/to/api-aponta
alembic upgrade head

# Staging
export DATABASE_SCHEMA=aponta_sefaz_staging
alembic upgrade head
```

### Option 2: Manual SQL Cleanup

```bash
# Via Docker
docker exec -it postgres-aponta psql -U api-aponta-user -d gestao_projetos

# Dentro do psql:
DROP SCHEMA IF EXISTS api_aponta CASCADE;
DROP SCHEMA IF EXISTS api_aponta_staging CASCADE;

-- Remover tabelas do public (se houver)
DROP TABLE IF EXISTS public.* CASCADE;

-- Verificar que está vazio
\dt public.*

-- Sair
\q
```

### Option 3: Via Script

```bash
bash scripts/migrate-schemas.sh
```

**O que o script faz**:
1. Migra dados de `api_aponta` para `aponta_sefaz` (se houver)
2. Migra dados de `api_aponta_staging` para `aponta_sefaz_staging` (se houver)
3. Remove schemas antigos
4. Limpa `public`
5. Define `search_path` correto

---

## Verification

### Check Current Schemas

```sql
-- Ver todos os schemas
SELECT schema_name FROM information_schema.schemata 
ORDER BY schema_name;

-- Ver tabelas por schema
SELECT table_schema, table_name FROM information_schema.tables 
WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
ORDER BY table_schema, table_name;
```

**Resultado esperado**:
```
     schema_name      
─────────────────────
 aponta_sefaz        
 aponta_sefaz_staging
(2 rows)
```

### Check Search Path

```sql
-- Ver search_path da database
SELECT datname, datacl FROM pg_database WHERE datname = 'gestao_projetos';

-- Ver search_path da sessão
SHOW search_path;
```

**Resultado esperado para produção**:
```
aponta_sefaz, aponta_sefaz_staging, public
```

**Resultado esperado para staging**:
```
aponta_sefaz_staging, public
```

### Verify No Data in Unwanted Schemas

```sql
-- Confirmar que api_aponta não existe
SELECT EXISTS(
    SELECT 1 FROM information_schema.schemata 
    WHERE schema_name = 'api_aponta'
) as api_aponta_exists;
-- Resultado: false

-- Confirmar que api_aponta_staging não existe
SELECT EXISTS(
    SELECT 1 FROM information_schema.schemata 
    WHERE schema_name = 'api_aponta_staging'
) as api_aponta_staging_exists;
-- Resultado: false

-- Confirmar que public está limpo
SELECT COUNT(*) FROM information_schema.tables 
WHERE table_schema = 'public' AND tablename NOT LIKE 'pg_%';
-- Resultado: 0
```

---

## Database Health Check

```bash
# Conectar e verificar
psql -h postgres-aponta \
     -U api-aponta-user \
     -d gestao_projetos \
     -c "
SELECT 
    schema_name,
    COUNT(*) as table_count
FROM information_schema.tables 
WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
GROUP BY schema_name
ORDER BY schema_name;
"
```

**Resultado esperado**:
```
       schema_name       | table_count
─────────────────────────┼─────────────
 aponta_sefaz            |           4
 aponta_sefaz_staging    |           4
(2 rows)
```

---

## Migration Timeline

### Phase 1: Code Changes (✅ Completed)
- [x] `app/config.py`: Default schema changed to `aponta_sefaz`
- [x] `.env`: Schema set to `aponta_sefaz`
- [x] `.env.staging`: Schema set to `aponta_sefaz_staging`
- [x] `scripts/init-schema.sql`: Creates new schemas, removes old ones
- [x] `docker-compose.yml`: Environment variable for production schema
- [x] `docker-compose.staging.yml`: Comment updated with correct schema names

### Phase 2: Data Migration (⏳ Pending - Choose one option)
- Option 1: Run `alembic upgrade head` (automatic via migration)
- Option 2: Run `scripts/migrate-schemas.sh` (manual SQL)
- Option 3: Manual `DROP SCHEMA` and cleanup

### Phase 3: Verification (⏳ Pending)
- Verify schemas exist only `aponta_sefaz` and `aponta_sefaz_staging`
- Confirm no tables in `api_aponta`, `api_aponta_staging`, or `public`
- Test API endpoints

### Phase 4: Deployment (⏳ Pending)
- Git push with all changes
- GitHub Actions redeploy to staging
- Monitor logs for successful migrations
- Test staging endpoints
- Deploy to production

---

## Commits

| Commit | Changes |
|--------|---------|
| Current | Config consolidation (app/config.py, .env, docker-compose, etc.) |
| Pending | Schema cleanup via Alembic migration |
| Pending | Deploy to staging |

---

## Troubleshooting

### ERROR: Cannot drop schema (tables depend on it)

**Cause**: Foreign keys between schemas

**Solution**: Drop in order of dependencies, or use `CASCADE`:
```sql
DROP SCHEMA IF EXISTS api_aponta CASCADE;
```

### Tables still exist in public

**Cause**: Search path or connections still pointing to old schema

**Solution**:
```sql
-- Disconnect all sessions
SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = 'gestao_projetos'
  AND pid <> pg_backend_pid();

-- Then drop
DROP SCHEMA IF EXISTS api_aponta CASCADE;
```

### "Unknown schema" Error

**Cause**: Application trying to use old schema name

**Solution**:
1. Verify `DATABASE_SCHEMA` is set correctly in `.env` or container env vars
2. Restart container to pick up new env var
3. Check logs: `docker logs api-aponta`

---

## References

- PostgreSQL Schema Documentation: https://www.postgresql.org/docs/current/ddl-schemas.html
- Alembic Migrations: https://alembic.sqlalchemy.org/
- Related Commits:
  - c5d3038: Alembic schema detection fix
  - 3104e90: PAT fallback authentication
  - 127ba78: Database schema documentation
