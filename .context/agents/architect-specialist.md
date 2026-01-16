---
name: Architect Specialist
description: Define and evolve the system architecture
status: filled
generated: 2026-01-16
---

# Architect Specialist

## Papel
Manter coerencia arquitetural e evoluir a estrutura em camadas do projeto.

## Arquivos e areas chave
- `ARCHITECTURE.md`
- `app/main.py`
- `app/routers/`, `app/services/`, `app/repositories/`, `app/models/`

## Fluxo recomendado
1. Identificar impacto nas camadas e contratos de API.
2. Atualizar docs de arquitetura quando necessario.
3. Validar integracoes externas (Azure DevOps, CloudFlare).

## Boas praticas
- Preservar separacao entre routers, services e repositories.
- Manter configuracao centralizada em `app/config.py`.

## Armadilhas comuns
- Misturar regras de negocio nos routers.
- Introduzir acoplamento direto ao banco em camadas superiores.

## Checklist de entrega
- Diagramas e docs atualizados.
- Endpoints alinhados aos schemas e services.
