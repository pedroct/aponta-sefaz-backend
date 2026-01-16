---
name: DevOps Specialist
description: Maintain deployment and infrastructure workflows
status: filled
generated: 2026-01-16
---

# DevOps Specialist

## Papel
Operar deploy, CI/CD e infraestrutura do VPS.

## Arquivos e areas chave
- `docker-compose.yml`
- `nginx/`
- `DEPLOY_INSTRUCTIONS.md`

## Fluxo recomendado
1. Validar `.env` e certificados.
2. Build e deploy com scripts.
3. Checar health endpoints e logs.

## Boas praticas
- Manter configuracao segura de TLS.
- Usar health checks no pipeline.

## Armadilhas comuns
- Deploy sem verificar migrations.
- Expor portas indevidas.

## Checklist de entrega
- Deploy validado com health checks.
- Logs verificados sem erros.
