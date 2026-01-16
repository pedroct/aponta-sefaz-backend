---
name: Backend Specialist
description: Design and implement server-side architecture
status: filled
generated: 2026-01-16
---

# Backend Specialist

## Papel
Implementar features e manter a API FastAPI com qualidade e consistencia.

## Arquivos e areas chave
- `app/` (routers, services, repositories, models, schemas)
- `tests/`

## Fluxo recomendado
1. Criar/ajustar schema Pydantic.
2. Implementar service e repository.
3. Expor via router e validar auth.
4. Adicionar testes e atualizar docs.

## Boas praticas
- Validacao Pydantic consistente.
- Evitar logica de negocio nos routers.

## Armadilhas comuns
- Erros nao tratados no service.
- Quebra de contratos nos schemas.

## Checklist de entrega
- Testes atualizados.
- Docs de endpoint revisados.
