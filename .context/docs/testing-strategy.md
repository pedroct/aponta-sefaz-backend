# Estrategia de testes

## Ferramentas
- Pytest + pytest-cov

## Escopo atual
- Health checks em `tests/test_health.py`.
- Fixtures em `tests/conftest.py`.

## Metas
- Cobertura de CRUD de atividades e projetos.
- Testes de integracao Azure DevOps (quando habilitado).

## Como rodar
- `pytest`
- `pytest --cov=app --cov-report=term`

## Observacoes
- Para testes com banco, use ambiente isolado e variaveis dedicadas.
