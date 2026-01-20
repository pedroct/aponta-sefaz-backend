# Handoff Claude Code – Correção Backend GET /api/v1/atividades

**Data:** 2026-01-18

## Contexto
- Backend dev: http://localhost:8000
- Auth: `AUTH_ENABLED=true` (Bearer obrigatório via `API_TOKEN`)
- Contrato: [FRONTEND_INTEGRATION_CONTEXT.md](FRONTEND_INTEGRATION_CONTEXT.md)

---

## Problema
`GET /api/v1/atividades` está retornando **500** (Internal Server Error).

**Impacto:** dropdown de atividades no modal não carrega, bloqueando criação de apontamentos.

---

## Estado atual (validação)
- `GET /api/v1/user` → **200**
- `GET /api/v1/work-items/search` → **200**
- `GET /api/v1/atividades` → **500**

---

## Expectativa de resposta
O frontend aceita **duas formas**:

1) **Lista direta de atividades**

**ou**

2) **Objeto com `items` e `total`**

**Formato recomendado (contrato):**
```json
{
  "items": [
    {
      "id": "dev-001",
      "nome": "Desenvolvimento",
      "descricao": "Desenvolvimento de features",
      "ativo": true,
      "projetos": [{ "id": "uuid", "nome": "DEV" }],
      "id_projeto": "uuid",
      "nome_projeto": "DEV",
      "criado_em": "ISO",
      "atualizado_em": "ISO"
    }
  ],
  "total": 1
}
```

---

## Possíveis causas do 500
- Tabela `atividades` não existe ou migração não aplicada.
- Seed inicial ausente (nenhuma atividade).
- Falha de consulta por filtros (`ativo`/`id_projeto`) ou relacionamento N:N.
- Middleware de auth falhando ao montar user/context.

---

## Objetivo
Corrigir o backend para `GET /api/v1/atividades` retornar com sucesso (200) no formato aceito pelo frontend.

---

## Validação completa (pós-ajustes)
- ✅ `GET /api/v1/projetos` → 200 (payload com `id` e `external_id`)
- ✅ `POST /api/v1/atividades` → 201 (atividade criada)
- ✅ `POST /api/v1/apontamentos` (work_item_id=4) → 201

**Endpoints pós-criação:**
- ✅ `GET /api/v1/apontamentos/work-item/4` → 200
- ✅ `GET /api/v1/apontamentos/work-item/4/resumo` → 200
- ✅ `GET /api/v1/apontamentos/work-item/4/azure-info` → 200

**Status:** Integração validada com sucesso.
