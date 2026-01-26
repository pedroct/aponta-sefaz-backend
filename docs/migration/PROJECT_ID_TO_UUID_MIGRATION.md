# Guia de Migração: Project ID para UUID

## Contexto

A aplicação passou por uma mudança importante no formato do `project_id`:

### Antes (Formato Antigo)
- **Tela Gestão de Apontamentos**: enviava o **nome do projeto** (ex: `"DEV"`)
- **Banco de dados**: armazenava `project_id: "DEV"`

### Agora (Formato Novo)
- **Modal do Work Item**: envia o **UUID do projeto** (ex: `"50a9ca09-710f-4478-8278-2d069902d2af"`)
- **Banco de dados**: deve armazenar `project_id: "50a9ca09-710f-4478-8278-2d069902d2af"`

## Problema

Os registros antigos no banco têm `project_id` inconsistente:

```sql
-- Registros antigos (Gestão de Apontamentos)
SELECT * FROM apontamentos WHERE project_id = 'DEV';

-- Registros novos (Modal do Work Item)
SELECT * FROM apontamentos WHERE project_id = '50a9ca09-710f-4478-8278-2d069902d2af';
```

Isso causa problemas nas queries do endpoint `/api/v1/timesheet` que filtra por `project_id`.

## Solução Implementada

### 1. Script de Migração Alembic

**Arquivo**: `alembic/versions/e5f6g7h8i9j0_migrate_project_id_to_uuid.py`

Este script:
- ✅ Identifica registros com `project_id` no formato antigo (não-UUID)
- ✅ Busca o UUID correspondente na tabela `projetos` pelo nome
- ✅ Atualiza todos os apontamentos para usar o UUID correto
- ✅ Fornece relatório detalhado da migração
- ✅ Permite rollback (downgrade)

**Como executar**:

```bash
# Em desenvolvimento (local)
cd /home/pedroctdev/apps/api-aponta-vps
alembic upgrade head

# Em staging (via SSH)
ssh -i C:\Users\pedro\.ssh\hostinger_github_deploy_key root@92.112.178.252
cd /home/ubuntu/aponta-sefaz/staging/backend
docker-compose exec backend alembic upgrade head

# Em produção (via SSH)
ssh -i C:\Users\pedro\.ssh\hostinger_github_deploy_key root@92.112.178.252
cd /home/ubuntu/aponta-sefaz/production/backend
docker-compose exec backend alembic upgrade head
```

### 2. Validação de UUID no Schema

**Arquivo**: `app/schemas/apontamento.py`

Adicionado validador `validate_project_id()` que:
- ✅ Valida formato UUID
- ✅ Permite nomes de projeto temporariamente (para compatibilidade)
- ✅ Emite mensagens de erro claras

```python
@field_validator("project_id")
@classmethod
def validate_project_id(cls, v: str) -> str:
    """Valida que project_id é um UUID válido."""
    if is_valid_uuid(v):
        return v
    
    # Permite nome durante transição
    if len(v) < 36 and not "-" in v:
        return v
    
    raise ValueError(f"project_id deve ser um UUID válido. Recebido: '{v}'")
```

### 3. Helper de Normalização

**Arquivo**: `app/utils/project_id_normalizer.py`

Funções utilitárias:
- `is_valid_uuid(value)`: Verifica se é UUID válido
- `normalize_project_id(project_id, db)`: Converte nome → UUID
- `validate_project_id_format(project_id)`: Valida formato apenas

### 4. Atualização dos Serviços

**Arquivos modificados**:
- `app/services/apontamento_service.py`
- `app/services/timesheet_service.py`

**Mudanças**:

#### ApontamentoService
```python
async def criar_apontamento(self, apontamento_data: ApontamentoCreate):
    # Normalizar project_id para UUID
    try:
        normalized_project_id = normalize_project_id(
            apontamento_data.project_id, self.db
        )
        apontamento_data.project_id = normalized_project_id
    except ValueError as e:
        logger.warning(f"Falha ao normalizar project_id: {e}")
```

#### TimesheetService
```python
def _get_apontamentos_semana(...):
    # Query que aceita ambos os formatos durante a transição
    query = self.db.query(Apontamento).filter(
        Apontamento.organization_name == organization,
        or_(
            Apontamento.project_id == project_normalized,  # UUID
            Apontamento.project_id == project,  # Formato antigo
        ),
        ...
    )
```

## Plano de Deploy

### Fase 1: Preparação (Local)
1. ✅ Testar migração em ambiente local
2. ✅ Verificar que todos os registros foram convertidos
3. ✅ Testar endpoints com ambos os formatos

```bash
# Local
cd /home/pedroctdev/apps/api-aponta-vps
alembic upgrade head

# Verificar migração
python -c "
from app.database import SessionLocal
from app.models.apontamento import Apontamento

db = SessionLocal()
# Contar registros antigos
antigos = db.query(Apontamento).filter(
    ~Apontamento.project_id.like('%-%')
).count()
print(f'Registros com formato antigo: {antigos}')
db.close()
"
```

### Fase 2: Deploy Staging
1. Fazer commit das mudanças
2. Push para branch `develop`
3. GitHub Actions executará deploy automático
4. Executar migração no container staging

```bash
# Commit e push
git add .
git commit -m "feat: normalizar project_id para UUID em apontamentos"
git push origin develop

# Aguardar deploy automático (.github/workflows/deploy-staging.yml)

# Conectar via SSH e executar migração
ssh -i C:\Users\pedro\.ssh\hostinger_github_deploy_key root@92.112.178.252
cd /home/ubuntu/aponta-sefaz/staging/backend
docker-compose exec backend alembic upgrade head

# Verificar logs
docker-compose logs backend | tail -50
```

### Fase 3: Testes em Staging
1. Testar tela Gestão de Apontamentos
2. Testar Modal do Work Item
3. Verificar endpoint `/api/v1/timesheet`
4. Confirmar que ambos os formatos funcionam

### Fase 4: Deploy Produção
1. Merge para branch principal (se aplicável)
2. GitHub Actions executará deploy em produção
3. Executar migração no container produção

```bash
# Push para produção
git push origin main

# Aguardar deploy automático (.github/workflows/deploy-production.yml)

# Conectar via SSH e executar migração
ssh -i C:\Users\pedro\.ssh\hostinger_github_deploy_key root@92.112.178.252
cd /home/ubuntu/aponta-sefaz/production/backend
docker-compose exec backend alembic upgrade head

# Monitorar logs
docker-compose logs backend -f
```

### Fase 5: Limpeza (Após Estabilização)
Depois de confirmar que tudo funciona:

1. Remover suporte ao formato antigo nos serviços
2. Tornar validação de UUID obrigatória
3. Remover queries com `or_()` no timesheet_service

## Comandos Úteis

### Verificar registros não migrados
```sql
-- Conectar ao banco
docker-compose exec db psql -U postgres -d aponta_sefaz

-- Listar project_id distintos não-UUID
SELECT DISTINCT project_id 
FROM apontamentos 
WHERE project_id NOT LIKE '%-%' 
  AND LENGTH(project_id) < 36;

-- Contar por formato
SELECT 
  CASE 
    WHEN project_id LIKE '%-%' THEN 'UUID'
    ELSE 'NOME'
  END as formato,
  COUNT(*) as total
FROM apontamentos
GROUP BY formato;
```

### Rollback da migração (se necessário)
```bash
# Reverter última migração
alembic downgrade -1

# Ou reverter para versão específica
alembic downgrade d4e5f6g7h8i9
```

### Logs de debug
```bash
# Staging
ssh -i C:\Users\pedro\.ssh\hostinger_github_deploy_key root@92.112.178.252
cd /home/ubuntu/aponta-sefaz/staging/backend
docker-compose logs backend | grep -i "project_id"

# Produção
cd /home/ubuntu/aponta-sefaz/production/backend
docker-compose logs backend | grep -i "project_id"
```

## Troubleshooting

### Problema: Migração falha ao não encontrar projeto
**Erro**: `Projeto 'DEV' não encontrado na tabela projetos`

**Solução**:
1. Verificar se o projeto existe na tabela `projetos`
2. Adicionar manualmente se necessário:

```sql
INSERT INTO projetos (id, external_id, nome, descricao)
VALUES (
  gen_random_uuid(),
  '50a9ca09-710f-4478-8278-2d069902d2af',
  'DEV',
  'Projeto de Desenvolvimento'
);
```

### Problema: Endpoints retornam dados vazios após migração
**Causa**: Frontend ainda envia nome do projeto em vez de UUID

**Solução Temporária**: O backend já está preparado para aceitar ambos os formatos

**Solução Definitiva**: Atualizar frontend para enviar UUID

### Problema: Erro de validação ao criar apontamento
**Erro**: `project_id deve ser um UUID válido`

**Causa**: Frontend enviando formato inválido

**Verificar**:
1. Certificar que o frontend envia `IProjectInfo.id` (UUID)
2. Não enviar `IProjectInfo.name` (string)

## Checklist de Deploy

- [ ] Executar migração local e verificar resultado
- [ ] Commit e push das mudanças
- [ ] Deploy automático staging concluído
- [ ] Executar migração em staging
- [ ] Testar ambas as telas em staging
- [ ] Verificar logs sem erros
- [ ] Deploy automático produção concluído
- [ ] Executar migração em produção
- [ ] Monitorar logs por 24h
- [ ] Confirmar que todos os registros foram migrados

## Contatos

Em caso de problemas durante o deploy:
- **Desenvolvedor**: Pedro (pedroct)
- **Servidor**: root@92.112.178.252
- **Repositório**: https://github.com/pedroct/aponta-sefaz-backend
