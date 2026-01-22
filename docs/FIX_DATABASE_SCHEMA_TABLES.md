# Database Schema Not Created - Fix Guide

## Problem

O erro `relation "api_aponta_staging.apontamentos" does not exist` indica que:

1. ✅ Schema `api_aponta_staging` foi criado
2. ❌ **As tabelas dentro do schema NÃO foram criadas**

## Root Cause

O problema estava em [alembic/versions/90324eefb107_initial_schema_api_aponta.py](alembic/versions/90324eefb107_initial_schema_api_aponta.py#L41):

```python
# ❌ ERRADO: Procura tabelas no schema 'public', não em 'aponta_sefaz_staging'
existing_tables = inspector.get_table_names()

# ✅ CORRETO: Procura no schema correto
existing_tables = inspector.get_table_names(schema=DB_SCHEMA)
```

## Solution

### Option 1: Automatic Reset (Recommended)

Execute o script para resetar o BD completamente:

```bash
# No container ou localmente
cd /path/to/api-aponta

# Carregar variáveis de ambiente
export $(cat .env.staging | xargs)

# Executar reset
bash scripts/reset-db-staging.sh
```

**O que esse script faz:**
1. Remove o schema `aponta_sefaz_staging` (e todas as tabelas)
2. Executa `alembic upgrade head` (recria schema e tabelas corretamente)
3. Verifica se as tabelas foram criadas

### Option 2: Manual Migration Run

```bash
# Conectar ao DB
psql -h postgres-aponta \
     -U api-aponta-user \
     -d gestao_projetos

# Dentro do psql:
-- Remover schema (opcional, vai reconstruir)
DROP SCHEMA IF EXISTS aponta_sefaz_staging CASCADE;

-- Sair do psql
\q
```

Depois:

```bash
# Executar migrations
cd /path/to/api-aponta
alembic upgrade head
```

### Option 3: Via Docker Compose

```bash
# Rebuild e reiniciar
docker compose -f docker-compose.staging.yml down
docker compose -f docker-compose.staging.yml up -d --build

# O start.sh vai executar as migrations automaticamente
# Verificar logs
docker logs api-aponta-staging
```

## Verification

### Check if tables exist:

```bash
psql -h postgres-aponta \
     -U api-aponta-user \
     -d gestao_projetos \
     -c "\dt aponta_sefaz_staging.*"
```

Expected output:
```
                  List of relations
       Schema       |      Name      | Type  |  Owner
───────────────────────────────────────────────────────
 aponta_sefaz_staging | apontamentos   | table | api-aponta-user
 aponta_sefaz_staging | atividades     | table | api-aponta-user
 aponta_sefaz_staging | atividades_pro | table | api-aponta-user
 aponta_sefaz_staging | projetos       | table | api-aponta-user
(4 rows)
```

### Test the API

```bash
curl -X GET "http://localhost:8000/api/v1/timesheet" \
  -H "Authorization: Bearer $(YOUR_JWT_TOKEN)"
```

Should return `200` with timesheet data, not `500`.

## Commits

- **c5d3038**: Fixed `inspector.get_table_names()` to use correct schema
- **3104e90**: PAT fallback authentication
- **cc2b972**: JWT vs PAT detection

## Timeline

1. ✅ **January 22**: JWT/PAT authentication fixed (Commit 3104e90)
2. ✅ **January 22**: Schema migration bug found (Log analysis)
3. ✅ **January 22**: Migration schema bug fixed (Commit c5d3038)
4. 📍 **NOW**: Execute migrations to create tables

## Next Steps

1. Choose an option above (Option 3 is easiest)
2. Execute migrations
3. Verify tables exist with `\dt` command
4. Test API endpoint
5. Report success!

## Troubleshooting

### Still getting "relation does not exist"?

1. **Verify schema exists:**
   ```sql
   SELECT schema_name FROM information_schema.schemata;
   ```
   Should show `aponta_sefaz_staging`

2. **Verify no tables in schema:**
   ```sql
   SELECT count(*) FROM information_schema.tables 
   WHERE table_schema = 'aponta_sefaz_staging';
   ```
   If returns `0`, migrations didn't run properly

3. **Check Alembic version:**
   ```bash
   alembic current
   ```
   Should show revision hash

4. **Check migration history:**
   ```bash
   alembic history
   ```

### Permissions error?

If getting permission error, check that `api-aponta-user` has rights:

```sql
GRANT ALL PRIVILEGES ON SCHEMA aponta_sefaz_staging TO "api-aponta-user";
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA aponta_sefaz_staging TO "api-aponta-user";
```

## References

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [PostgreSQL Schema Documentation](https://www.postgresql.org/docs/current/ddl-schemas.html)
- [SQLAlchemy Inspector](https://docs.sqlalchemy.org/en/20/core/reflection.html)
