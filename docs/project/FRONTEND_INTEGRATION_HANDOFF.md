# Handoff Claude Code - Integração Frontend ↔ Backend

**Data:** 2026-01-18

## Contexto
Projeto: **fe-aponta** (frontend-only).
Backend dev: http://localhost:8000, `AUTH_ENABLED=true`.
Base URL no frontend: `http://localhost:8000/api/v1`.
Autenticação via Bearer token (`API_TOKEN`).

## Ajustes já feitos no frontend
- Centralização de base URL e headers em `api-client.ts` com helpers `getApiUrl()` e `buildApiHeaders()` (usa `VITE_API_URL` e `VITE_API_TOKEN`).
- Hooks usando base URL + headers:
  - `use-api.ts`
  - `use-atividades.ts`
  - `use-current-user.ts`
  - `use-search-work-items.ts`
- Search de work items usa parâmetros `query`, `project_id`, `organization_name` conforme [FRONTEND_INTEGRATION_CONTEXT.md](FRONTEND_INTEGRATION_CONTEXT.md).

## Validação atual (token no .env — NÃO compartilhar)
- `GET /api/v1/user` → **200**
- `GET /api/v1/work-items/search` → **200**
- `GET /api/v1/atividades` → **200**

## Impacto
- Dropdown de atividades no modal **ok**.
- Criação de apontamentos **ok**.

## Próximo passo
- Garantir que o frontend repasse `x-custom-header` quando estiver disponível (7pace/Timehub) para `displayName` completo.
- Validar `POST /api/v1/apontamentos` e endpoints de resumo se houver mudanças no fluxo.

## Nota sobre 7pace
Os endpoints do 7pace/Timehub são externos à API Aponta. Ver lista em [FRONTEND_INTEGRATION_CONTEXT.md](FRONTEND_INTEGRATION_CONTEXT.md).

## Referência de contrato
- [FRONTEND_INTEGRATION_CONTEXT.md](FRONTEND_INTEGRATION_CONTEXT.md)
