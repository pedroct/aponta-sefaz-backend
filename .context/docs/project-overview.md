# Visao geral do projeto

## Objetivo
API backend em FastAPI para gerenciar atividades e projetos integrados ao Azure DevOps, com deploy em VPS e protecao via CloudFlare.

## Principais capacidades
- CRUD de atividades e projetos
- Integracao com Azure DevOps (validacao de token e sincronizacao)
- Health checks e documentacao OpenAPI
- Deploy com Docker Compose + Nginx
- Migracoes com Alembic

## Publico alvo
- Extensao/servico que consome dados de projetos/atividades no Azure DevOps
- Time de backend/DevOps responsavel por VPS/CloudFlare

## Dependencias e integracoes
- PostgreSQL 15
- Azure DevOps REST API
- CloudFlare (SSL/TLS e protecao)
- Nginx como proxy reverso

## Inicio rapido (dev)
1. Configure `.env` conforme `README.md`.
2. Suba o stack com Docker Compose.
3. Rode migrations com Alembic.
4. Acesse `/docs` para Swagger.

## Referencias
- `README.md`
- `WORKSPACE_CONTEXT.md`
- `ARCHITECTURE.md`
