# Contexto de Integração Frontend → Backend (API Aponta VPS)

**Última atualização:** 2026-01-18

## 1) Objetivo
Este documento prepara o contexto para iniciar a integração do frontend com o backend FastAPI da API Aponta. Deve ser usado como ponto de partida para implementar chamadas HTTP, autenticação, modelos e tratamento de erros.

---

## 2) Base URL e Documentação
- **Base URL (produção):** https://api-aponta.pedroct.com.br
- **Swagger:** https://api-aponta.pedroct.com.br/docs
- **ReDoc:** https://api-aponta.pedroct.com.br/redoc

---

## 3) Autenticação
Todos os endpoints (exceto health e API info) exigem autenticação.

**Header:**
```
Authorization: Bearer <TOKEN>
```

**Token esperado:**
- PAT do Azure DevOps **ou** token obtido via Azure DevOps Extension SDK.

**Observação:**
- Quando `AUTH_ENABLED=false` no backend (desenvolvimento), o backend usa um usuário mock.

### 3.1) Header `x-custom-header` (7pace → Backend)
O backend aceita um header opcional `x-custom-header` com JSON em base64 para enriquecer o perfil do usuário.

**Formato do payload (JSON antes de base64):**
- `User-Unique-Name` (ex: email)
- `User-Name` (nome completo)
- `User-Email`
- `Account-Name`

**Regras de prioridade:**
1. Se presente, `User-Name` **sobrepõe** `displayName` retornado pela API de perfil.
2. Se presente, `User-Email` **sobrepõe** `emailAddress`.

**Quando usar:**
- Extensão 7pace/Timehub (Azure DevOps) normalmente fornece esse header.
- Se o frontend não tiver acesso a esse header, a API ainda resolve o usuário via Azure Profile API.

---

## 4) Endpoints essenciais

### Health / Info
- `GET /`
- `GET /health`
- `GET /healthz`
- `GET /api/v1`

### Atividades
- `GET /api/v1/atividades` (paginado)
- `GET /api/v1/atividades/{id}`
- `POST /api/v1/atividades`
- `PUT /api/v1/atividades/{id}`
- `DELETE /api/v1/atividades/{id}`

### Apontamentos
- `POST /api/v1/apontamentos`
- `GET /api/v1/apontamentos/work-item/{work_item_id}`
- `GET /api/v1/apontamentos/work-item/{work_item_id}/resumo`
- `GET /api/v1/apontamentos/work-item/{work_item_id}/azure-info`
- `GET /api/v1/apontamentos/{apontamento_id}`
- `PUT /api/v1/apontamentos/{apontamento_id}`
- `DELETE /api/v1/apontamentos/{apontamento_id}`

### Projetos
- `GET /api/v1/projetos` (cache local)
- `POST /api/v1/integracao/sincronizar` (sincroniza do Azure)

### Integração Azure DevOps
- `GET /api/v1/integracao/projetos` (consulta direta ao Azure)

### Work Items
- `GET /api/v1/work-items/search`
  - Query: `query`, `project_id`, `organization_name`, `limit`

### Usuário
- `GET /api/v1/user`

---

## 4.1) Endpoints 7pace (externos)
Os links abaixo **não pertencem** à API Aponta. São endpoints do 7pace/Timehub usados pela extensão do Azure DevOps.

**Hubs e páginas (hosted):**
- `https://{{account.name}}.timehub.7pace.com/`
- `https://{{account.name}}.timehub.7pace.com/Weekly`
- `https://{{account.name}}.timehub.7pace.com/Timesheet/Timesheet`
- `https://{{account.name}}.timehub.7pace.com/TimesExplorer`
- `https://{{account.name}}.timehub.7pace.com/Approval`
- `https://{{account.name}}.timehub.7pace.com/Iterations`
- `https://{{account.name}}.timehub.7pace.com/Reporting`
- `https://{{account.name}}.timehub.7pace.com/BudgetsList`
- `https://{{account.name}}.timehub.7pace.com/Configuration`
- `https://{{account.name}}.timehub.7pace.com/Apps`

**Controles/dialogs (hosted):**
- `https://{{account.name}}.timehub.7pace.com/Account/AuthVso?id={{Id}}`
- `https://{{account.name}}.timehub.7pace.com/Import/CopyPaste`
- `https://{{account.name}}.timehub.7pace.com/Import`
- `https://{{account.name}}.timehub.7pace.com/Integration/Tab`
- `https://{{account.name}}.timehub.7pace.com/Integration/StartTrackingButtonDetails`
- `https://{{account.name}}.timehub.7pace.com/Integration/AddTimePopupDialog/{{id}}`

**On-Premises:**
- `on-prem-blank/OnPremBlank.html`

---

## 5) Modelos relevantes (resumo)

### Atividade (resposta)
- `id: UUID`
- `nome: string`
- `descricao: string | null`
- `ativo: boolean`
- `projetos: Array<{ id: UUID, nome: string }>`
- `id_projeto?: UUID` (retrocompatibilidade)
- `nome_projeto?: string | null` (retrocompatibilidade)
- `criado_em: ISO datetime`
- `atualizado_em: ISO datetime`

**Importante (N:N):**
- Para criação/atualização use `ids_projetos: UUID[]` (mínimo 1).
- `id_projeto` ainda é aceito, mas não é o formato recomendado.

### Apontamento (request)
- `work_item_id: int`
- `project_id: string` (ID ou nome do projeto Azure DevOps)
- `organization_name: string`
- `usuario_id: string`
- `usuario_nome: string`
- `usuario_email?: string`
- `data_apontamento: YYYY-MM-DD`
- `duracao: "HH:mm"` (ex: 02:30)
- `id_atividade: UUID`
- `comentario?: string`

### Apontamento (response)
Inclui campos acima +:
- `duracao_horas: number`
- `atividade: { id: UUID, nome: string }`
- `criado_em`, `atualizado_em`

### Work Item (search response)
- `id: number`
- `title: string`
- `type: string`
- `project: string`
- `url: string`
- `originalEstimate?: number`
- `completedWork?: number`
- `remainingWork?: number`
- `state: string`

### User (response)
- `id: string`
- `displayName: string`
- `emailAddress: string | null`
- `avatarUrl: string | null`

---

## 6) Padrões de resposta e erros

**Erro padrão:**
```json
{ "detail": "Mensagem do erro" }
```

**Erro de validação (422):**
```json
{
  "detail": [
    {
      "loc": ["body", "campo"],
      "msg": "mensagem",
      "type": "tipo"
    }
  ]
}
```

---

## 7) Paginação
Listas usam:
- `skip` (default 0)
- `limit` (default 100, max 1000)

---

## 8) CORS (produção)
Origens liberadas:
- https://api-aponta.pedroct.com.br
- https://dev.azure.com
- https://vsassets.io
- https://sefaz-ceara.gallerycdn.vsassets.io
- https://sefaz-ceara-lab.gallerycdn.vsassets.io

---

## 9) Recomendações para o frontend
1. Centralizar HTTP client (fetch/axios) com injeção do Bearer Token.
2. Criar types/interfaces para Atividade, Apontamento, Projeto, WorkItem e User.
3. Padronizar tratamento de erros (401/403/422/500).
4. Adicionar helpers para paginação (skip/limit).
5. Normalizar `duracao` em HH:mm no formulário.
6. Usar `ids_projetos` em toda criação/atualização de atividade.
7. Se disponível, repassar `x-custom-header` (base64 JSON) para o backend para garantir `displayName` completo.

---

## 10) Referências
- [README.md](../../README.md)
- [API_DOCUMENTATION.md](../api/API_DOCUMENTATION.md)
- [ARCHITECTURE.md](../architecture/ARCHITECTURE.md)
