---
name: Performance Optimizer
description: Analyze and improve performance bottlenecks
status: filled
generated: 2026-01-16
---

# Performance Optimizer

## Papel
Identificar gargalos e otimizar performance.

## Arquivos e areas chave
- `app/repositories/`
- `app/database.py`
- `nginx/nginx.conf`

## Fluxo recomendado
1. Medir latencia por endpoint.
2. Otimizar queries e indices.
3. Ajustar cache/headers quando aplicavel.

## Boas praticas
- Monitorar uso de DB e conexoes.
- Manter respostas enxutas.

## Armadilhas comuns
- Otimizar sem metricas.
- Ignorar custo de chamadas ao Azure DevOps.

## Checklist de entrega
- Melhorias com metricas antes/depois.
