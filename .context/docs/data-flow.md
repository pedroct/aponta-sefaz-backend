# Fluxo de dados

## Modelos e schemas
- **Atividade** (`app/models/atividade.py`) e schemas em `app/schemas/atividade.py`.
- **Projeto** (`app/models/projeto.py`).

## Endpoints principais
- `/api/v1/atividades` (CRUD)
- `/api/v1/projetos` (listagem)
- `/api/v1/integracao/*` (Azure DevOps)
- `/health`, `/healthz` e `/` (health)

## Pipeline de transformacao
1. Request -> validacao Pydantic
2. Regras de negocio em `app/services/`
3. Persistencia via `app/repositories/`
4. Resposta -> schema de saida

## Estado e persistencia
- API stateless
- Estado persistido em PostgreSQL
- Configuracoes em `.env`

## Integracoes externas
- Azure DevOps REST API (validacao de token e sincronizacao)
- CloudFlare (entrada externa)

## Observacoes
- Erros sao tratados em `app/main.py` (handler global).
- Logs e health checks suportam monitoramento basico.
