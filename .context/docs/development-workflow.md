# Workflow de desenvolvimento

## Branching
- Fluxo principal em `develop` e `main`.
- Novas features em branch dedicada.

## Ambiente local
- Python 3.12 + Docker Compose.
- Configure `.env` conforme `README.md`.

## Qualidade
- Formatar: Black
- Imports: isort
- Lint: Flake8
- Tipos: MyPy

## Testes
- `pytest` para suite principal.
- Ver `tests/` para exemplos.

## Deploy
- Scripts em `scripts/` e `QUICK_DEPLOY.sh`.
- Documentacao em `DEPLOY_INSTRUCTIONS.md`.
