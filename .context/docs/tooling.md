# Ferramentas

## Infra
- Docker e Docker Compose
- Nginx (config em `nginx/nginx.conf`)
- CloudFlare (docs em `CLOUDFLARE_SETUP.md`)

## Banco
- Alembic para migracoes
- Scripts de deploy executam migrations

## Scripts
- `QUICK_DEPLOY.sh`, `manual_deploy.sh`, `scripts/deploy.sh`
- `scripts/collect_metrics.py` para metricas pontuais

## Qualidade
- Black, isort, Flake8, MyPy
- Pytest + pytest-cov
