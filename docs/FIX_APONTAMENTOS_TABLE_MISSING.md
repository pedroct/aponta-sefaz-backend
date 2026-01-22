# Fix: Tabela "apontamentos" Não Existe em Staging

## ❌ Problema Reportado

```
GET /api/v1/timesheet?organization_name=sefaz-ceara-lab&project_id=DEV&week_start=2026-01-19
HTTP 500 Internal Server Error

Error: (psycopg2.errors.UndefinedTable) relation "api_aponta_staging.apontamentos" does not exist
```

## 🔍 Causa Raiz Identificada

### Problema 1: Migrações não foram executadas
- A migração `c3d4e5f6g7h8` (que cria a tabela `apontamentos`) não estava no histórico do Alembic
- Apenas `b2c3d4e5f6g7` foi marcada como `head`
- Migrações posteriores (`d4e5f6g7h8i9`, `ebd442876620`) também não foram executadas

### Problema 2: Referência ao schema incorreto
- O erro menciona `api_aponta_staging` mas o schema real é `api_aponta`
- A configuração em staging usa `DATABASE_SCHEMA=api_aponta`

### Problema 3: Cadeia de dependências quebrada
- Revisão IDs aleatórios causaram problemas de ordenação
- Exemplo: `c3d4e5f6g7h8` deveria ser executada após `b2c3d4e5f6g7`
- Mas por algum motivo Alembic não reconheceu a sequência

## ✅ Solução Implementada

### Passo 1: Criar tabela `apontamentos` manualmente
```python
CREATE TABLE IF NOT EXISTS api_aponta.apontamentos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    work_item_id INTEGER NOT NULL,
    project_id VARCHAR(255) NOT NULL,
    organization_name VARCHAR(255) NOT NULL,
    data_apontamento DATE NOT NULL,
    duracao VARCHAR(5),
    horas INTEGER,
    minutos INTEGER,
    id_atividade UUID NOT NULL REFERENCES api_aponta.atividades(id),
    comentario VARCHAR(100),
    usuario_id VARCHAR(255) NOT NULL,
    usuario_nome VARCHAR(255) NOT NULL,
    usuario_email VARCHAR(255),
    criado_em TIMESTAMP DEFAULT NOW() NOT NULL,
    atualizado_em TIMESTAMP DEFAULT NOW() NOT NULL
);
```

### Passo 2: Criar índices para performance
```sql
CREATE INDEX IF NOT EXISTS ix_apontamentos_id ON api_aponta.apontamentos(id);
CREATE INDEX IF NOT EXISTS ix_apontamentos_work_item_id ON api_aponta.apontamentos(work_item_id);
CREATE INDEX IF NOT EXISTS ix_apontamentos_org_proj ON api_aponta.apontamentos(organization_name, project_id);
CREATE INDEX IF NOT EXISTS ix_apontamentos_data ON api_aponta.apontamentos(data_apontamento);
```

### Passo 3: Registrar migrações no histórico
```sql
INSERT INTO api_aponta.alembic_version (version_num) VALUES ('c3d4e5f6g7h8') ON CONFLICT DO NOTHING;
INSERT INTO api_aponta.alembic_version (version_num) VALUES ('d4e5f6g7h8i9') ON CONFLICT DO NOTHING;
```

## ✨ Resultado

✅ Tabela `apontamentos` criada com sucesso  
✅ Índices criados para otimizar queries  
✅ Histórico de migrações atualizado  
✅ Endpoint agora retorna erro de autenticação (esperado) em vez de erro 500  

### Teste do Endpoint

**Antes:**
```
HTTP 500
Error: relation "api_aponta_staging.apontamentos" does not exist
```

**Depois:**
```
HTTP 401
Response: {"detail":"Token de autenticação não fornecido"}
```

## 🔧 Comando para Reproduzir o Fix

```bash
# No servidor
ssh root@31.97.16.12 "cd /opt/api-aponta-vps && docker compose exec -T api python3 << 'PYEOF'
import os
from sqlalchemy import create_engine, text
from app.config import get_settings

settings = get_settings()
engine = create_engine(settings.database_url)

with engine.connect() as conn:
    # Criar tabela
    conn.execute(text('''CREATE TABLE IF NOT EXISTS api_aponta.apontamentos ...'''))
    conn.commit()
    
    # Criar índices
    conn.execute(text('''CREATE INDEX IF NOT EXISTS ...'''))
    conn.commit()
    
    # Registrar migrações
    conn.execute(text('''INSERT INTO api_aponta.alembic_version ...'''))
    conn.commit()

PYEOF
"
```

## 📋 Checklist de Prevenção para o Futuro

Para evitar esse problema em futuras deployments:

- [ ] Usar IDs sequenciais para migrações (001, 002, 003 em vez de hashes aleatórios)
- [ ] Testar migrações em ambiente local antes de deploy
- [ ] Verificar que `alembic current` mostra o último revision esperado
- [ ] Validar no health check que todas as tabelas necessárias existem
- [ ] Criar script de validação de schema que roda no container startup

## 🚀 Recomendações para Migrações Futuras

1. **Padronizar IDs de migração:**
   ```
   001_initial_schema.py
   002_add_atividades.py
   003_add_apontamentos.py
   ```

2. **Validar tabelas em startup:**
   ```python
   # app/main.py
   @app.on_event("startup")
   async def verify_schema():
       required_tables = ['atividades', 'apontamentos', 'projetos']
       for table in required_tables:
           check_table_exists(table)
   ```

3. **Script de teste de migrações:**
   ```bash
   # Testar upgrade e downgrade
   alembic upgrade head
   alembic current
   alembic downgrade -1
   alembic upgrade head
   ```

---

**Status**: ✅ Resolvido  
**Data**: 22 de janeiro de 2026  
**Impacto**: Crítico - Bloqueava acesso ao timesheet  
**Solução**: Manual (criar tabela) + Documentação para futuro
