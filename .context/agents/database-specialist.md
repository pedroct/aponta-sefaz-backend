---
name: Database Specialist
description: Manage schemas, migrations, and database performance
status: filled
generated: 2026-01-16
---

# Database Specialist

## Papel
Manter schema, migracoes e performance do PostgreSQL.

## Arquivos e areas chave
- `alembic/`
- `app/models/`
- `app/database.py`

## Fluxo recomendado
1. Atualizar modelos.
2. Gerar migration Alembic.
3. Validar constraints e indices.

## Boas praticas
- Manter migrations idempotentes e versionadas.
- Revisar indices para queries criticas.

## Armadilhas comuns
- Alteracoes sem migration.
- Quebra de compatibilidade de dados.

## Checklist de entrega
- Migration testada.
- Compatibilidade retroativa considerada.
