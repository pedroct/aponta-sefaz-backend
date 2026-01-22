# Correção: Erro de Migração Alembic no Deploy

## Problema Identificado

**Erro no GitHub Actions Deploy (2026-01-22):**
```
sqlalchemy.exc.ProgrammingError: 
relation "api_aponta_staging.alembic_version" does not exist
```

### Raiz da Causa

Conflito de sequência durante inicialização do container:

1. **scripts/init-schema.sql** executa primeiro
   - Deleta schema `api_aponta_staging` com `DROP SCHEMA ... CASCADE`
   - Cria novo schema `aponta_sefaz_staging`

2. **Alembic** tenta executar (após init-schema)
   - Procura `alembic_version` table no schema deletado
   - **FALHA**: Schema `api_aponta_staging` não existe mais

3. **Versão quebrada em Alembic**: `cleanup_old_1234567890`
   - Tentava dropbar schemas antigos via Alembic
   - Mas Alembic já estava configurado para usar o schema antigo
   - Criava referência circular impossível de resolver

## Solução Implementada

### ✅ Commit c520d34: Removeu migração conflitante

**O que foi feito:**
- Deletado arquivo: `alembic/versions/cleanup_old_1234567890_cleanup_old_schemas.py`
- Deixar `scripts/init-schema.sql` como **única fonte de verdade** para limpeza

### Nova Sequência Correta

```
┌─────────────────────────────────────────┐
│ 1. Container Inicia                     │
└──────────────┬──────────────────────────┘
               ▼
┌─────────────────────────────────────────┐
│ 2. scripts/init-schema.sql Executa      │
│    - DROP api_aponta                    │
│    - DROP api_aponta_staging            │
│    - CREATE aponta_sefaz                │
│    - CREATE aponta_sefaz_staging        │
└──────────────┬──────────────────────────┘
               ▼
┌─────────────────────────────────────────┐
│ 3. Alembic Upgrade Executa              │
│    - app/main.py -> init_db()          │
│    - alembic upgrade head               │
│    - Schemas já existem ✅              │
│    - alembic_version criada OK ✅       │
└──────────────┬──────────────────────────┘
               ▼
┌─────────────────────────────────────────┐
│ 4. API Inicia com Sucesso               │
│    - Tabelas já existem                 │
│    - Migrations aplicadas               │
└─────────────────────────────────────────┘
```

## Arquivos Alterados

| Arquivo | Ação | Razão |
|---------|------|-------|
| `alembic/versions/cleanup_old_1234567890_cleanup_old_schemas.py` | 🗑️ DELETADO | Conflitava com `init-schema.sql` |
| `scripts/init-schema.sql` | ✅ Mantido | Única responsável por cleanup |
| `alembic/env.py` | ✅ Mantido | Já correto, usa `version_table_schema` |

## Verificação Pós-Deploy

### 1. Verificar Schemas Existentes

```bash
psql -h postgres-aponta -U api-aponta-user -d gestao_projetos -c "
SELECT schema_name, 
       (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = s.schema_name) as table_count
FROM information_schema.schemata s
WHERE schema_name NOT IN ('pg_catalog', 'information_schema')
ORDER BY schema_name;"
```

**Esperado:**
```
       schema_name       | table_count
─────────────────────────┼─────────────
 aponta_sefaz            |           4
 aponta_sefaz_staging    |           4
(2 rows)
```

### 2. Verificar Legados Deletados

```bash
psql -h postgres-aponta -U api-aponta-user -d gestao_projetos -c "
SELECT EXISTS(SELECT 1 FROM information_schema.schemata WHERE schema_name = 'api_aponta') as api_aponta_exists,
       EXISTS(SELECT 1 FROM information_schema.schemata WHERE schema_name = 'api_aponta_staging') as api_aponta_staging_exists;"
```

**Esperado:** `false | false`

### 3. Verificar Alembic Version

```bash
psql -h postgres-aponta -U api-aponta-user -d gestao_projetos -c "
SELECT * FROM aponta_sefaz.alembic_version;
SELECT * FROM aponta_sefaz_staging.alembic_version;"
```

**Esperado:** Ambas mostram versão mais recente (ex: `d4e5f6g7h8i9`)

## Próximos Passos

### Para Staging
```bash
docker compose -f docker-compose.staging.yml down
docker compose -f docker-compose.staging.yml up -d --build
# Aguarde 20 segundos
curl -X GET "http://localhost:8000/api/v1/apontamentos" \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

### Para Produção
```bash
# Merge para main
git merge develop
# GitHub Actions executará automaticamente
# Alembic iniciará sem conflitos
```

## Lições Aprendidas

1. **Duas fontes de verdade são ruins**: Alembic + init-schema.sql competindo
2. **init-schema.sql é mais apropriada**: Roda ANTES da aplicação
3. **Alembic para estrutura**: Melhor para criar tabelas/colunas
4. **SQL puro para setup**: Melhor para limpeza/schemas

## Commits Relacionados

- ✅ **8eda447**: Criou migração Alembic (foi necessário entender o problema)
- ✅ **65add80**: Melhorou script manual (contexto for learning)
- ✅ **d13e449**: Documentou opções (útil mesmo após remoção)
- ✅ **c520d34**: Removeu conflito (SOLUÇÃO FINAL)

## Status

- ✅ Problema identificado
- ✅ Solução implementada
- ✅ Commit merged para develop
- ⏳ Próximo deploy testará automaticamente

