# Configuração de Autenticação: JWT vs PAT

## Problema

O frontend (Azure DevOps Extension) envia um **JWT (App Token)** para autenticar o usuário. Porém:

- ✅ JWT é válido para autenticar o **usuário** na API (`/api/v1/user`)
- ❌ JWT **NÃO** pode fazer chamadas para as **APIs do Azure DevOps** (WIQL, Work Items, etc.)

Para chamar as APIs do Azure DevOps, é necessário um **PAT (Personal Access Token)**.

## Solução Implementada

O serviço `TimesheetService` agora implementa **fallback de autenticação**:

1. **Preferência**: Usa `AZURE_DEVOPS_PAT` configurado no `.env` (if configured)
2. **Fallback**: Usa JWT se PAT não estiver configurado
3. **Comportamento esperado**:
   - Se PAT é válido → API chama Azure DevOps com sucesso ✅
   - Se PAT está vazio → JWT tenta chamar Azure DevOps → erro 500 ❌

## Configuração Requerida

### Para Staging (`/.env.staging`)

```bash
AZURE_DEVOPS_PAT=sua_chave_pat_aqui
```

### Como Obter um PAT

1. Vá para https://dev.azure.com/sefaz-ceara-lab/_usersSettings/tokens
2. Clique em "New Token"
3. Defina:
   - **Name**: `aponta-backend-staging`
   - **Organization**: `sefaz-ceara-lab`
   - **Expiration**: 1 year (ou conforme politica)
   - **Scopes**: Marque pelo menos:
     - ✅ Work Items (Read & write)
     - ✅ Build (Read)
4. Copie o token (pode copiar apenas uma vez!)
5. Cole no `.env.staging`:
   ```
   AZURE_DEVOPS_PAT=seu_token_aqui
   ```

### Para Produção (`/.env`)

```bash
AZURE_DEVOPS_PAT=seu_pat_producao_aqui
```

## Implementação Técnica

**Arquivo**: `app/services/timesheet_service.py`

```python
class TimesheetService:
    def __init__(self, db: Session, token: str | None = None):
        # PAT é preferido (para chamadas de API)
        # JWT é fallback (para autenticação do usuário)
        self.api_token = settings.azure_devops_pat or token or ""

    async def _get_work_items_hierarchy(self, ...):
        # Detectar tipo de token
        is_jwt = self.api_token.count(".") == 2 if self.api_token else False
        
        if is_jwt:
            # JWT usa Bearer auth (mas falha na Azure DevOps API)
            headers = {"Authorization": f"Bearer {self.api_token}"}
        else:
            # PAT usa Basic auth
            pat_encoded = base64.b64encode(f":{self.api_token}".encode()).decode()
            headers = {"Authorization": f"Basic {pat_encoded}"}
```

## Detecção de Token

| Token | Partes | Auth Type | Uso |
|-------|--------|-----------|-----|
| **JWT** | 3 (xx.yy.zz) | Bearer | Autenticar usuário na API |
| **PAT** | 1 | Basic | Chamar APIs do Azure DevOps |

## Diagnosticando Problemas

### Erro 500 em `/api/v1/timesheet`

**Causa**: PAT não configurado, JWT tentando chamar Azure DevOps API

**Solução**:
1. Verifique `.env.staging`: `AZURE_DEVOPS_PAT` está vazio?
2. Obtenha um PAT válido (veja "Como Obter um PAT" acima)
3. Configure em `.env.staging`
4. Redeploy: `git push origin develop` → GitHub Actions executa
5. Teste: `GET /api/v1/timesheet?organization_name=sefaz-ceara-lab&project_id=DEV&week_start=2026-01-19`

### Verificar nos Logs

```bash
docker logs aponta-api-staging

# Procure por:
# ✅ "Usando PAT para autenticação" → Correto
# ❌ "Usando JWT (App Token) para autenticação" → PAT não configurado
```

## Commits Relacionados

- **cc2b972**: Adicionada detecção de JWT vs PAT
- **3104e90**: Refatorado para usar `api_token` (PAT com fallback para JWT)

## Próximos Passos

1. ⚠️ **CRITICAL**: Configurar `AZURE_DEVOPS_PAT` em `.env.staging`
2. Fazer commit da config (ou usar secrets do GitHub Actions)
3. Redeploy
4. Testar endpoint `/api/v1/timesheet`
5. Verificar logs para confirmar uso de PAT
