# Como Executar o Script de Migração de Schemas

## Problema
Ao executar `bash scripts/migrate-schemas.sh` via PowerShell do Windows, o sistema tenta traduzir o caminho do WSL e falha.

## Solução

### Opção 1: Via Docker (Recomendado se container está rodando)

```bash
# Se o container está rodando, execute dentro dele
docker exec -it api-aponta-staging bash -c "cd /app && bash scripts/migrate-schemas.sh"
```

### Opção 2: Via WSL Bash Direto

```powershell
# No PowerShell, execute via wsl
wsl bash -c "cd /home/pedroctdev/apps/api-aponta && bash scripts/migrate-schemas.sh"
```

### Opção 3: Dentro do WSL Terminal

```bash
# Abra um terminal WSL (Ubuntu-24.04) e execute:
cd /home/pedroctdev/apps/api-aponta
bash scripts/migrate-schemas.sh
```

### Opção 4: Via psql Direto (Sem script)

```bash
# Se apenas quer executar a migração, use psql diretamente:
psql -h postgres-aponta \
     -U api-aponta-user \
     -d gestao_projetos \
     -f /tmp/migrate.sql
```

---

## Requisitos

Para executar o script, você precisa:

1. ✅ **psql instalado** no ambiente
   ```bash
   # Se não estiver:
   apt-get install postgresql-client
   ```

2. ✅ **Variáveis de ambiente configuradas**:
   ```bash
   export DATABASE_HOST=postgres-aponta
   export DATABASE_USER=api-aponta-user
   export DATABASE_PASSWORD=fs-eWwus9wPgHPT-C6
   export DATABASE_NAME=gestao_projetos
   ```

3. ✅ **Acesso ao PostgreSQL** (container rodando ou rede acessível)

---

## Alternativa: Deixar Alembic Fazer

Se preferir, **a próxima vez que os containers iniciarem**, a migration cleanup será executada automaticamente via Alembic:

```bash
# Iniciar containers (vai executar alembic upgrade head automaticamente)
docker compose -f docker-compose.staging.yml up -d --build

# Verificar logs
docker logs api-aponta-staging | grep -i "schema\|migration"
```

---

## Verificar Resultado

Após executar (por qualquer método), verifique se funcionou:

```bash
psql -h postgres-aponta \
     -U api-aponta-user \
     -d gestao_projetos \
     -c "
SELECT schema_name, 
       (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = s.schema_name) as table_count
FROM information_schema.schemata s
WHERE schema_name NOT IN ('pg_catalog', 'information_schema')
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

## Próxima Vez

Não precisa executar o script manualmente - o Alembic já tem a migration `cleanup_old_1234567890` que será executada automaticamente no próximo `upgrade head`.

Basta:
```bash
docker compose -f docker-compose.staging.yml down
docker compose -f docker-compose.staging.yml up -d --build
```
