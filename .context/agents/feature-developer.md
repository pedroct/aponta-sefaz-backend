---
name: Feature Developer
description: Deliver new features aligned with project conventions
status: filled
generated: 2026-01-16
---

# Feature Developer

## Papel
Adicionar features mantendo padroes do projeto.

## Arquivos e areas chave
- `app/routers/`
- `app/services/`
- `app/repositories/`
- `app/schemas/`

## Fluxo recomendado
1. Definir contrato do endpoint.
2. Implementar service e repository.
3. Adicionar testes e atualizar docs.

## Boas praticas
- Preferir pequenas mudancas isoladas.
- Reutilizar services quando possivel.

## Armadilhas comuns
- Alterar schema sem migration.
- Ignorar casos de erro.

## Checklist de entrega
- Endpoints documentados.
- Testes cobrindo novos fluxos.
