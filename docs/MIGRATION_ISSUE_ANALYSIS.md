# Problema de Migrações em Staging - Resolução

## Erro Reportado
```
(psycopg2.errors.UndefinedTable) relation "api_aponta_staging.apontamentos" does not exist
```

## Causa Raiz

O Alembic não está executando as migrações `c3d4e5f6g7h8`, `d4e5f6g7h8i9` devido a problemas na cadeia de dependências.

### Histórico Atual
```
ebd442876620 -> 90324eefb107 -> a1b2c3d4e5f6 -> b2c3d4e5f6g7 [HEAD]
```

### Migrações Faltando
```
c3d4e5f6g7h8 (cria tabela apontamentos) <- DEVERIA estar aqui
d4e5f6g7h8i9 (altera apontamentos) <- DEVERIA estar aqui
```

## Solução

O problema é que a migração `c3d4e5f6g7h8` não foi registrada no histórico do Alembic. Precisamos:

1. Recriar as migrações em uma ordem lógica
2. Usar numeração sequencial: 001, 002, 003, etc. (ao invés de IDs aleatórios)
3. Garantir que todas as migrações sejam executadas em sequence

## Ações Necessárias

1. ✅ **Backup do banco**: Criar snapshot antes de alterações
2. ✅ **Corrigir migrações**: Regenerar com IDs sequenciais
3. ✅ **Resetar histórico**: `alembic stamp ebd442876620` 
4. ✅ **Executar novamente**: `alembic upgrade head`

## Implementação da Solução

Ver `DEPLOYMENT_FIX_MIGRATION_ERROR.md` para os passos completos.
