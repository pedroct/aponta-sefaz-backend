# Autenticação - Sistema Aponta

**Última atualização:** 21/01/2026  
**Status:** ✅ Implementado e funcionando

---

## ⚠️ Importante: App Token vs PAT

> **O App Token JWT NÃO pode ser usado para chamar APIs do Azure DevOps.**
> 
> Ele serve apenas para identificar o usuário. Para chamar WIQL, buscar Work Items, etc.,
> é necessário usar o **PAT do backend** (`settings.azure_devops_pat`).

---

## Visão Geral

O sistema utiliza **dois tipos de autenticação** com responsabilidades distintas:

| Token | Origem | Responsabilidade |
|-------|--------|------------------|
| **App Token JWT** | `getAppToken()` do SDK | Identificar o usuário |
| **PAT** (Personal Access Token) | Variável de ambiente | Acessar APIs do Azure DevOps |

---

## Fluxo de Autenticação

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

---

## 1. App Token JWT (Identificação do Usuário)

### Origem
- Obtido via `VSS.getAppToken()` no frontend (Azure DevOps Extension SDK)
- Token JWT assinado com HS256

### Validação no Backend
- Usa `AZURE_EXTENSION_SECRET` para validar assinatura
- Issuer esperado: `app.vstoken.visualstudio.com`
- Audience: App ID da extensão (`560de67c-a2e8-408a-86ae-be7ea6bd0b7a`)

### Claims do Token
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

### Código de Validação (`app/auth.py`)
```python
import jwt

def validate_app_token_jwt(token: str) -> dict | None:
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
        
    return payload
```

---

## 2. PAT (Acesso às APIs do Azure DevOps)

### Por que usar PAT?
- O App Token JWT **não pode** ser usado para chamar APIs do Azure DevOps
- O PAT é uma "chave de leitura" compartilhada pelo backend

### Configuração
```env
AZURE_DEVOPS_PAT=xxx...xxx
AZURE_DEVOPS_ORG_URL=https://dev.azure.com/sefaz-ceara-lab
```

### Uso nos Serviços
```python
class TimesheetService:
    def __init__(self, db: Session, token: str | None = None):
        self.db = db
        # IMPORTANTE: Para chamadas à API do Azure DevOps, usar PAT do backend
        # O token do usuário (App Token JWT) não tem permissão para WIQL
        self.token = settings.azure_devops_pat or token

    def _get_auth_header(self) -> dict[str, str]:
        """Header para APIs do Azure DevOps usando PAT."""
        token = self._azure_api_token
        if not token:
            return {}
        pat_encoded = base64.b64encode(f":{token}".encode()).decode()
        return {"Authorization": f"Basic {pat_encoded}"}
```

---

## 3. Variáveis de Ambiente

### Obrigatórias para Autenticação
```env
# Secret da extensão (obter em https://aka.ms/vsmarketplace-manage)
AZURE_EXTENSION_SECRET=9TbeZUXAQW5BJANtPVl5ipNYknRutZLBQpIqenb8zv6IqNgajTixJQQJ99CAACAAAAAAAAAAAAAEAZDOCIUB

# App ID da extensão (fixo)
AZURE_EXTENSION_APP_ID=560de67c-a2e8-408a-86ae-be7ea6bd0b7a

# PAT para acesso às APIs do Azure DevOps
AZURE_DEVOPS_PAT=Ass5XrpyvjnQZrDj8SfIebZb0YS60s5fpMywA8Bdl67Ox2pURlhEJQQJ99CAACAAAAAq8a74AAASAZDO4LTQ

# URL da organização
AZURE_DEVOPS_ORG_URL=https://dev.azure.com/sefaz-ceara-lab
```

---

## 4. Fluxo Completo

### Frontend (timesheet.html)
```javascript
VSS.ready(function() {
    var webContext = VSS.getWebContext();
    
    // Usar getAppToken() para autenticação com backend próprio
    VSS.getAppToken().then(function(appToken) {
        var params = new URLSearchParams({
            organization: webContext.account.name,
            project: webContext.project.name,
            userId: webContext.user.id,
            token: appToken  // App Token JWT (421 chars)
        });
        
        iframe.src = baseUrl + '?' + params.toString();
    });
});
```

### Backend (auth.py)
```python
async def validate_azure_token(request, credentials):
    token = credentials.credentials
    
    # Detectar se é App Token JWT (curto, ~400-500 chars)
    if _is_app_token_jwt(token):
        payload = validate_app_token_jwt(token)
        
        if payload:
            user_id = payload.get("nameid")
            return AzureDevOpsUser(
                id=user_id,
                display_name=f"User-{user_id[:8]}",  # Placeholder
                token=token,
            )
    
    # Fallback para PAT (desenvolvimento)
    return await _fetch_user_profile(token)
```

### Endpoint /user (busca perfil real)
```python
@router.get("/user")
async def get_user(current_user = Depends(get_current_user)):
    # Se nome é placeholder, buscar perfil completo no Azure DevOps
    if current_user.display_name.startswith("User-"):
        azure_service = AzureService(token=current_user.token)
        profile = await azure_service.get_user_profile(current_user.id)
        return UserResponse(
            id=current_user.id,
            displayName=profile.get("displayName"),
            emailAddress=profile.get("emailAddress"),
            avatarUrl=profile.get("avatarUrl"),
        )
    return UserResponse(...)
```

### Serviços (timesheet_service.py, etc.)
```python
# Autenticação: user_id vem do JWT
user_id = current_user.id  # "08347002-d37b-6380-a5a7-645420d92a52"

# Acesso ao Azure DevOps: usa PAT do backend
headers = self._get_auth_header()  # Usa AZURE_DEVOPS_PAT
response = await client.post(wiql_url, headers=headers, ...)
```

---

## 5. Diferença entre getAccessToken() e getAppToken()

| Método | Uso | Tamanho | Validação |
|--------|-----|---------|-----------|
| `getAccessToken()` | Chamar APIs do Azure DevOps diretamente | ~1100 chars | Azure DevOps valida |
| `getAppToken()` | Autenticar com backend próprio | ~421 chars | Backend valida com secret |

**Importante:** Usamos `getAppToken()` porque precisamos validar o usuário no nosso backend.

---

## 6. Busca de Perfil do Usuário

O App Token JWT contém apenas o `nameid` (GUID do usuário), não o nome real.
Para obter o nome completo, usamos a **API de Member Entitlements**:

### API Utilizada
```
GET https://vsaex.dev.azure.com/{org}/_apis/userentitlements/{userId}?api-version=7.1-preview.3
```

### Resposta
```json
{
  "user": {
    "displayName": "PEDRO CICERO TEIXEIRA",
    "mailAddress": "pedro.teixeira@sefaz.ce.gov.br"
  }
}
```

### Implementação (`app/services/azure.py`)
```python
async def get_user_profile(self, user_id: str) -> dict:
    """Busca o perfil do usuário no Azure DevOps pelo ID."""
    org_name = self._resolve_org_name(None)
    
    # 1. API de Member Entitlements (retorna nome completo real)
    url = f"https://vsaex.dev.azure.com/{org_name}/_apis/userentitlements/{user_id}?api-version=7.1-preview.3"
    response = await self._request("GET", url)
    
    if response.status_code == 200:
        data = response.json()
        user_data = data.get("user", {})
        return {
            "displayName": user_data.get("displayName"),
            "emailAddress": user_data.get("mailAddress"),
            "avatarUrl": None,
        }
    
    # Fallback para outras APIs...
```

---

## 7. Arquivos Relevantes

- `app/auth.py` - Validação de tokens e autenticação
- `app/config.py` - Configurações (secrets, PAT)
- `app/routers/user.py` - Endpoint /user com busca de perfil
- `app/services/azure.py` - Uso do PAT + busca de perfil do usuário
- `app/services/timesheet_service.py` - Uso do PAT para APIs
- `app/services/apontamento_service.py` - Uso do PAT para APIs

---

## 8. Troubleshooting

### Erro 401 nas chamadas ao Azure DevOps
- Verificar se `AZURE_DEVOPS_PAT` está configurado e válido
- Verificar se o PAT tem permissões de leitura para Work Items

### App Token JWT inválido
- Verificar se `AZURE_EXTENSION_SECRET` está correto
- Obter em: https://aka.ms/vsmarketplace-manage > Botão direito > Certificate

### Token expirado
- App Token expira em ~70 minutos
- Frontend deve renovar automaticamente via `getAppToken()`
