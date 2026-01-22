---
type: doc
name: security
description: Security policies, authentication, secrets management, and compliance requirements
category: security
generated: 2026-01-22
status: filled
scaffoldVersion: "2.0.0"
---
## Security & Compliance Notes

O Sistema Aponta utiliza um modelo de autenticação dupla para garantir segurança e integração com o Azure DevOps.

## ⚠️ Regra de Ouro da Autenticação

> **O App Token JWT NÃO pode ser usado para chamar APIs do Azure DevOps.**
> 
> Ele serve apenas para identificar o usuário. Para chamar WIQL, buscar Work Items, etc.,
> é necessário usar o **PAT do backend** (`settings.azure_devops_pat`).

## Authentication Flow

```
┌─────────────────┐      App Token JWT       ┌─────────────────┐
│    Frontend     │ ───────────────────────> │     Backend     │
│  (Extensão)     │   (421 chars, HS256)     │    (FastAPI)    │
└─────────────────┘                          └────────┬────────┘
                                                      │
                                    ┌─────────────────┼─────────────────┐
                                    │                 │                 │
                                    ▼                 ▼                 ▼
                             1. Valida JWT     2. Extrai claims   3. Usa PAT
                             (AZURE_SECRET)    nameid = user_id   p/ Azure API
                                                      │
                                                      ▼
                                              4. Salva apontamento
                                              com user_id no banco
```

## Token Types

| Token | Origem | Responsabilidade | Tamanho |
|-------|--------|------------------|---------|
| **App Token JWT** | `VSS.getAppToken()` | Identificar o usuário | ~421 chars |
| **PAT** (Personal Access Token) | Variável de ambiente | Acessar APIs do Azure DevOps | N/A |

## App Token JWT Claims

```json
{
  "nameid": "08347002-d37b-6380-a5a7-645420d92a52",  // ID do usuário
  "tid": "e9ad8643-b5e9-447f-b324-d78e61d7ed84",     // Tenant ID
  "jti": "5a3a4469-9908-446f-bd72-837bc8bb9f39",     // JWT ID único
  "iss": "app.vstoken.visualstudio.com",             // Issuer
  "aud": "560de67c-a2e8-408a-86ae-be7ea6bd0b7a",     // App ID
  "nbf": 1769006959,                                  // Not Before
  "exp": 1769011159                                   // Expiration (~70 min)
}
```

## JWT Validation (app/auth.py)

```python
payload = jwt.decode(
    token,
    settings.azure_extension_secret,
    algorithms=["HS256"],
    audience=settings.azure_extension_app_id,
    options={
        "require": ["exp", "nameid", "iss", "aud"],
        "verify_exp": True,
    }
)

if payload.get("iss") != "app.vstoken.visualstudio.com":
    return None
```

## Secrets & Sensitive Data

### Required Environment Variables

| Variable | Purpose | Location |
|----------|---------|----------|
| `AZURE_EXTENSION_SECRET` | Validar assinatura do JWT | VPS `/root/staging.env` |
| `AZURE_EXTENSION_APP_ID` | Audience do JWT | Fixo: `560de67c-a2e8-408a-86ae-be7ea6bd0b7a` |
| `AZURE_DEVOPS_PAT` | Acesso às APIs do Azure | VPS `/root/staging.env` |
| `DATABASE_URL` | Conexão PostgreSQL | VPS `/root/staging.env` |
| `DATABASE_SCHEMA` | Schema do banco | `aponta_sefaz_staging` ou `aponta_sefaz` |

### Secrets Location

- **Staging**: `/root/staging.env`
- **Produção**: `/root/prod.env`
- **Obtendo Extension Secret**: https://aka.ms/vsmarketplace-manage > Botão direito > Certificate

## PAT Usage in Services

```python
class AzureService:
    def __init__(self, token: str):
        self.token = token
        # Para chamadas à API do Azure DevOps, usar PAT do backend
        self._azure_api_token = settings.azure_devops_pat or token

    async def _request(self, method: str, url: str, json: dict | None = None):
        pat_encoded = base64.b64encode(f":{self._azure_api_token}".encode()).decode()
        headers = {"Authorization": f"Basic {pat_encoded}"}
        # ...
```

## CORS Configuration

```python
CORS_ORIGINS=https://staging-aponta.treit.com.br,https://dev.azure.com,https://*.visualstudio.com
```

## Troubleshooting

### Erro 401 nas chamadas ao Azure DevOps
- Verificar se `AZURE_DEVOPS_PAT` está configurado e válido
- Verificar se o PAT tem permissões de leitura para Work Items
- Garantir que os serviços usam `settings.azure_devops_pat` (não o token do usuário)

### App Token JWT inválido
- Verificar se `AZURE_EXTENSION_SECRET` está correto
- Obter em: https://aka.ms/vsmarketplace-manage > Botão direito > Certificate

### Token expirado
- App Token expira em ~70 minutos
- Frontend deve renovar automaticamente via `getAppToken()`

## Related Resources

- [architecture.md](./architecture.md)
- [development-workflow.md](./development-workflow.md)
