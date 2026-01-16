# Arquitetura

## Visao geral
A arquitetura segue camadas (routers -> services -> repositories -> models), com FastAPI rodando em container e exposta via Nginx. O trafego externo passa pelo CloudFlare com SSL/TLS.

## Componentes principais
- **CloudFlare**: TLS, protecao e proxy.
- **Nginx**: reverse proxy, rate limiting e compressao.
- **FastAPI** (`app/main.py`): API, auth e roteamento.
- **Banco** (PostgreSQL 15): persistencia.
- **Migracoes** (`alembic/`): versionamento de schema.

## Fluxo de dados (alto nivel)
1. Cliente -> CloudFlare -> Nginx
2. Nginx -> FastAPI
3. FastAPI valida, aplica regras e acessa repositorios
4. Repositorios interagem com PostgreSQL
5. Resposta retorna via Nginx/CloudFlare

## Padroes e decisoes
- **Arquitetura em camadas** para separar responsabilidades.
- **Repository pattern** em `app/repositories/`.
- **Schemas Pydantic** em `app/schemas/`.
- **Settings** centralizado em `app/config.py`.

## Stack e racional
- **FastAPI + Pydantic**: performance e validacao automatica.
- **SQLAlchemy + Alembic**: ORM e migracoes consistentes.
- **Docker Compose**: ambiente repetivel.
- **Nginx + CloudFlare**: seguranca e performance.

## Referencias
- `ARCHITECTURE.md`
- `README.md`
