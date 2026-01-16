# Guia de Contribuição

Obrigado por considerar contribuir com a API Aponta! Este documento fornece diretrizes para contribuir com o projeto.

## 📋 Índice

- [Código de Conduta](#código-de-conduta)
- [Como Posso Contribuir?](#como-posso-contribuir)
- [Configuração do Ambiente](#configuração-do-ambiente)
- [Fluxo de Trabalho](#fluxo-de-trabalho)
- [Padrões de Código](#padrões-de-código)
- [Conventional Commits](#conventional-commits)
- [Testes](#testes)
- [Documentação](#documentação)
- [Pull Requests](#pull-requests)

---

## 📜 Código de Conduta

### Nosso Compromisso

No interesse de promover um ambiente aberto e acolhedor, nós, como contribuidores e mantenedores, nos comprometemos a fazer da participação em nosso projeto e nossa comunidade uma experiência livre de assédio para todos.

### Padrões Esperados

**Comportamentos positivos:**
- ✅ Usar linguagem acolhedora e inclusiva
- ✅ Respeitar pontos de vista e experiências diferentes
- ✅ Aceitar críticas construtivas graciosamente
- ✅ Focar no que é melhor para a comunidade
- ✅ Mostrar empatia com outros membros

**Comportamentos inaceitáveis:**
- ❌ Uso de linguagem ou imagens sexualizadas
- ❌ Trolling, comentários insultuosos/depreciativos
- ❌ Assédio público ou privado
- ❌ Publicar informações privadas de outros sem permissão
- ❌ Outras condutas não profissionais

### Aplicação

Instâncias de comportamento abusivo, assediante ou inaceitável podem ser reportadas entrando em contato com contato@pedroct.com.br.

---

## 🤝 Como Posso Contribuir?

### Reportar Bugs

Antes de criar um bug report, verifique se já não existe uma issue similar.

**Como escrever um bom bug report:**

```markdown
**Descrição do Bug**
Uma descrição clara e concisa do bug.

**Como Reproduzir**
Passos para reproduzir o comportamento:
1. Vá para '...'
2. Clique em '...'
3. Faça scroll até '...'
4. Veja o erro

**Comportamento Esperado**
O que você esperava que acontecesse.

**Screenshots**
Se aplicável, adicione screenshots.

**Ambiente:**
 - OS: [e.g. Ubuntu 22.04]
 - Python: [e.g. 3.12.0]
 - Versão: [e.g. 0.1.0]

**Contexto Adicional**
Qualquer outra informação relevante.
```

### Sugerir Melhorias

**Template para sugestão de feature:**

```markdown
**A feature está relacionada a um problema?**
Descrição clara do problema. Ex: Fico frustrado quando [...]

**Descreva a solução desejada**
Descrição clara do que você quer que aconteça.

**Descreva alternativas consideradas**
Outras soluções ou features que você considerou.

**Contexto Adicional**
Screenshots, mockups, etc.
```

### Primeira Contribuição

Procure por issues com as tags:
- `good first issue` - Boas para iniciantes
- `help wanted` - Precisamos de ajuda
- `documentation` - Melhorias de documentação

---

## 💻 Configuração do Ambiente

### 1. Fork e Clone

```bash
# Fork no GitHub (clique no botão Fork)

# Clone seu fork
git clone https://github.com/SEU-USUARIO/api-aponta-vps.git
cd api-aponta-vps

# Adicione o upstream
git remote add upstream https://github.com/pedroct/api-aponta-vps.git
```

### 2. Ambiente de Desenvolvimento Local

#### Opção A: Com Docker (Recomendado)

```bash
# Copie o .env de exemplo
cp .env.example .env

# Edite as variáveis
nano .env

# Inicie os containers
docker compose up -d

# Ver logs
docker compose logs -f
```

#### Opção B: Ambiente Python Local

```bash
# Crie ambiente virtual
python3.12 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Instale dependências
pip install -r requirements.txt

# Instale ferramentas de dev
pip install pytest pytest-asyncio pytest-cov black isort flake8 mypy

# Configure o banco (PostgreSQL deve estar rodando)
export DATABASE_URL="postgresql://user:pass@localhost:5432/aponta_db"

# Execute migrations
alembic upgrade head

# Inicie a aplicação
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Verificar Instalação

```bash
# Health check
curl http://localhost:8000/health

# Docs
open http://localhost:8000/docs
```

---

## 🔄 Fluxo de Trabalho

### Git Flow

Usamos uma versão simplificada do Git Flow:

```
main          ← Produção (apenas releases)
  ↑
develop       ← Desenvolvimento (branch padrão)
  ↑
feature/*     ← Novas features
fix/*         ← Bug fixes
hotfix/*      ← Correções urgentes em produção
```

### Branches

**Nomenclatura:**
```bash
feature/nome-da-feature      # Nova funcionalidade
fix/descricao-do-bug         # Correção de bug
hotfix/correcao-urgente      # Correção urgente
docs/atualizacao-readme      # Documentação
refactor/melhoria-codigo     # Refatoração
test/adiciona-testes         # Testes
chore/atualiza-deps          # Manutenção
```

**Exemplos:**
```bash
git checkout -b feature/adiciona-autenticacao-jwt
git checkout -b fix/corrige-validacao-data
git checkout -b docs/atualiza-api-docs
```

### Workflow Completo

```bash
# 1. Atualize develop
git checkout develop
git pull upstream develop

# 2. Crie sua branch
git checkout -b feature/minha-feature

# 3. Faça suas alterações
# ... código ...

# 4. Teste localmente
pytest
black app/
isort app/
flake8 app/

# 5. Commit (use Conventional Commits)
git add .
git commit -m "feat: adiciona autenticação JWT"

# 6. Push para seu fork
git push origin feature/minha-feature

# 7. Abra Pull Request no GitHub
# - Base: develop
# - Compare: feature/minha-feature
```

---

## 📝 Padrões de Código

### Python Style Guide

Seguimos **PEP 8** com algumas adaptações:

```python
# ✅ BOM
def calculate_total_price(items: list[Item]) -> Decimal:
    """
    Calculate the total price of items.

    Args:
        items: List of items to calculate total

    Returns:
        Total price as Decimal

    Raises:
        ValueError: If items list is empty
    """
    if not items:
        raise ValueError("Items list cannot be empty")

    return sum(item.price for item in items)


# ❌ RUIM
def calc(items):
    return sum([item.price for item in items])
```

### Formatação

Usamos ferramentas automáticas:

```bash
# Black - Formatação de código (line length: 100)
black app/ --line-length 100

# isort - Ordenação de imports
isort app/

# Flake8 - Linting
flake8 app/ --max-line-length 100

# MyPy - Type checking
mypy app/
```

### Configuração Pre-commit (Recomendado)

```bash
# Instale pre-commit
pip install pre-commit

# Configure hooks
cat > .pre-commit-config.yaml <<EOF
repos:
  - repo: https://github.com/psf/black
    rev: 24.1.1
    hooks:
      - id: black
        language_version: python3.12

  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        args: ['--max-line-length=100']
EOF

# Instale os hooks
pre-commit install

# Teste
pre-commit run --all-files
```

### Estrutura de Código

```python
# app/routers/exemplo.py

"""
Router para operações de exemplo.

Este módulo contém endpoints relacionados a exemplos.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.exemplo import ExemploCreate, ExemploResponse
from app.services.exemplo import ExemploService

router = APIRouter(prefix="/api/v1/exemplos", tags=["Exemplos"])


@router.get("/", response_model=list[ExemploResponse])
async def list_exemplos(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Lista todos os exemplos com paginação.

    Args:
        skip: Número de registros para pular
        limit: Número máximo de registros a retornar
        db: Sessão do banco de dados

    Returns:
        Lista de exemplos
    """
    service = ExemploService(db)
    return service.get_all(skip=skip, limit=limit)
```

---

## 🎯 Conventional Commits

Usamos [Conventional Commits](https://conventionalcommits.org/) para mensagens de commit estruturadas.

### Formato

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types

| Type | Descrição | Exemplo |
|------|-----------|---------|
| `feat` | Nova funcionalidade | `feat: adiciona endpoint de relatórios` |
| `fix` | Correção de bug | `fix: corrige validação de email` |
| `docs` | Documentação | `docs: atualiza README com exemplos` |
| `style` | Formatação | `style: aplica black e isort` |
| `refactor` | Refatoração | `refactor: simplifica lógica de cálculo` |
| `test` | Testes | `test: adiciona testes para atividades` |
| `chore` | Manutenção | `chore: atualiza dependências` |
| `perf` | Performance | `perf: otimiza query de listagem` |
| `ci` | CI/CD | `ci: adiciona GitHub Actions` |
| `build` | Build | `build: atualiza Dockerfile` |
| `revert` | Reverter | `revert: reverte commit abc123` |

### Exemplos

```bash
# Feature simples
feat: adiciona autenticação JWT

# Feature com scope
feat(auth): implementa refresh token

# Fix com corpo
fix: corrige timezone em datas

Anteriormente as datas estavam sendo salvas em UTC sem conversão.
Agora todas as datas são convertidas para o timezone configurado.

Closes #123

# Breaking change
feat!: remove suporte a Python 3.11

BREAKING CHANGE: A versão mínima do Python agora é 3.12

# Múltiplos footers
feat: adiciona integração com GitHub

Reviewed-by: Pedro CT
Refs: #456
```

### Usar Commitizen

```bash
# Instale commitizen
pip install commitizen

# Faça commit interativo
cz commit

# Bump de versão automático
cz bump --changelog
```

---

## 🧪 Testes

### Escrever Testes

Todos os PRs devem incluir testes.

```python
# tests/test_atividades.py

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_list_atividades():
    """Testa listagem de atividades."""
    response = client.get("/api/v1/atividades")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_atividade():
    """Testa criação de atividade."""
    payload = {
        "titulo": "Nova Atividade",
        "descricao": "Descrição da atividade",
        "status": "pendente"
    }
    response = client.post("/api/v1/atividades", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["titulo"] == payload["titulo"]


@pytest.mark.parametrize("invalid_data", [
    {},
    {"titulo": ""},
    {"titulo": "Teste"},  # Falta descrição
])
def test_create_atividade_invalid_data(invalid_data):
    """Testa validação de dados inválidos."""
    response = client.post("/api/v1/atividades", json=invalid_data)
    assert response.status_code == 422
```

### Executar Testes

```bash
# Todos os testes
pytest

# Com coverage
pytest --cov=app --cov-report=html

# Testes específicos
pytest tests/test_atividades.py

# Com verbose
pytest -v

# Apenas testes rápidos
pytest -m "not slow"
```

### Coverage Mínimo

- **Geral:** 80%
- **Funções críticas:** 100%

---

## 📚 Documentação

### Docstrings

Use Google Style:

```python
def process_data(data: dict, validate: bool = True) -> ProcessedData:
    """
    Process input data and return structured result.

    Args:
        data: Dictionary containing raw data to process
        validate: Whether to validate data before processing (default: True)

    Returns:
        ProcessedData object with validated and transformed data

    Raises:
        ValueError: If data is invalid and validate=True
        KeyError: If required keys are missing from data

    Examples:
        >>> data = {"name": "Test", "value": 100}
        >>> result = process_data(data)
        >>> print(result.name)
        'Test'
    """
    pass
```

### README Updates

Atualize README.md se sua mudança:
- Adiciona nova funcionalidade
- Muda comportamento existente
- Adiciona dependências
- Muda requisitos

---

## 🔀 Pull Requests

### Checklist antes do PR

- [ ] Código segue os padrões do projeto
- [ ] Executei black, isort, flake8
- [ ] Adicionei testes para novas funcionalidades
- [ ] Todos os testes estão passando
- [ ] Atualizei a documentação
- [ ] Usei Conventional Commits
- [ ] PR tem título descritivo
- [ ] Descrição explica o "porquê" e "como"

### Template de PR

```markdown
## Descrição

Breve descrição das mudanças.

## Motivação e Contexto

Por que essa mudança é necessária? Qual problema resolve?

Closes #123

## Tipo de Mudança

- [ ] Bug fix (non-breaking change)
- [ ] New feature (non-breaking change)
- [ ] Breaking change (fix or feature)
- [ ] Documentation update

## Como Testar

1. Passo 1
2. Passo 2
3. Verificar X

## Screenshots (se aplicável)

## Checklist

- [ ] Código segue style guide
- [ ] Self-review realizado
- [ ] Comentários adicionados em código complexo
- [ ] Documentação atualizada
- [ ] Testes adicionados
- [ ] Todos os testes passam
- [ ] Conventional Commits usado
```

### Processo de Review

1. **Automated Checks:** CI/CD deve passar
2. **Code Review:** Pelo menos 1 aprovação
3. **Testes:** Todos os testes devem passar
4. **Conflicts:** Resolver conflitos com develop
5. **Merge:** Squash and merge para develop

---

## ❓ Perguntas?

- **Issues:** [GitHub Issues](https://github.com/pedroct/api-aponta-vps/issues)
- **Discussões:** [GitHub Discussions](https://github.com/pedroct/api-aponta-vps/discussions)
- **Email:** contato@pedroct.com.br

---

**Obrigado por contribuir! 🎉**
