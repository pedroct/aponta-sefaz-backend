# Arquitetura do Sistema Aponta

**Última atualização:** 21/01/2026

---

## Visão Geral

Sistema de apontamento de horas integrado ao Azure DevOps, composto por:

- **Frontend**: Extensão Azure DevOps (iframe com React/Vite)
- **Backend**: API FastAPI (Python)
- **Banco de Dados**: PostgreSQL
- **Infraestrutura**: VPS com Docker + Nginx

---

## Componentes

```
┌─────────────────────────────────────────────────────────────────┐
│                        Azure DevOps                              │
│  ┌─────────────────┐                                            │
│  │  Extensão Aponta │◄──── vss-extension.json                   │
│  │  (timesheet.html)│                                            │
│  └────────┬────────┘                                            │
│           │ iframe                                               │
│           ▼                                                      │
│  ┌─────────────────┐                                            │
│  │ Frontend React  │◄──── https://staging-aponta.treit.com.br   │
│  │ (Vite + TS)     │                                            │
│  └────────┬────────┘                                            │
└───────────┼─────────────────────────────────────────────────────┘
            │ HTTPS (App Token JWT)
            ▼
┌─────────────────────────────────────────────────────────────────┐
│                        VPS (92.112.178.252)                      │
│                                                                  │
│  ┌─────────────────┐     ┌─────────────────┐                    │
│  │     Nginx       │────▶│  API FastAPI    │                    │
│  │  (Proxy Reverso)│     │  (Python 3.12)  │                    │
│  └─────────────────┘     └────────┬────────┘                    │
│                                   │                              │
│                          ┌────────┴────────┐                    │
│                          ▼                 ▼                    │
│                   ┌──────────┐      ┌──────────────┐            │
│                   │PostgreSQL│      │ Azure DevOps │            │
│                   │   (DB)   │      │     API      │            │
│                   └──────────┘      └──────────────┘            │
│                                     (via PAT)                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Estrutura do Backend

```
app/
├── __init__.py
├── main.py              # FastAPI app, routers, CORS
├── config.py            # Settings (env vars)
├── database.py          # SQLAlchemy session
├── auth.py              # Autenticação (JWT + PAT)
├── supabase_client.py   # Cliente Supabase (opcional)
│
├── models/              # SQLAlchemy models
│   ├── apontamento.py
│   ├── atividade.py
│   ├── projeto.py
│   └── ...
│
├── schemas/             # Pydantic schemas
│   ├── apontamento.py
│   ├── atividade.py
│   ├── timesheet.py
│   └── ...
│
├── repositories/        # Acesso a dados
│   ├── apontamento.py
│   └── atividade.py
│
├── routers/             # Endpoints da API
│   ├── apontamentos.py
│   ├── atividades.py
│   ├── projetos.py
│   ├── timesheet.py       # Endpoint /timesheet (grade semanal)
│   ├── user.py
│   └── work_items.py
│
└── services/            # Lógica de negócio
    ├── apontamento_service.py
    ├── timesheet_service.py  # Monta hierarquia Work Items + apontamentos (usa PAT)
    ├── azure.py              # APIs Azure DevOps + busca de perfil (usa PAT)
    └── projeto_service.py
```

---

## Containers Docker

### Staging
| Container | Imagem | Porta |
|-----------|--------|-------|
| api-aponta-staging | staging-api:latest | 8001 → 8000 |
| fe-aponta-staging | staging-frontend | 80 |
| nginx-aponta | nginx:alpine | 80/443 |
| postgres-aponta | postgres:15-alpine | 5432 |

### Produção
| Container | Imagem | Porta |
|-----------|--------|-------|
| api-aponta-prod | production-api:latest | 8000 → 8000 |
| fe-aponta-prod | production-frontend | 80 |

---

## Banco de Dados

### Schema: `aponta_sefaz_staging` (staging) / `aponta_sefaz` (produção)

#### Tabelas
| Tabela | Descrição |
|--------|-----------|
| `apontamentos` | Registros de horas apontadas |
| `atividades` | Tipos de atividades (Planning, Development, etc.) |
| `projetos` | Projetos cadastrados |
| `atividade_projeto` | Relação N:N entre atividades e projetos |
| `alembic_version` | Controle de migrações |

#### Tabela: `apontamentos`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | UUID | PK |
| usuario_id | VARCHAR | ID do usuário Azure DevOps |
| usuario_nome | VARCHAR | Nome do usuário |
| usuario_email | VARCHAR | Email do usuário |
| work_item_id | INTEGER | ID do Work Item |
| organization_name | VARCHAR | Organização Azure DevOps |
| project_id | VARCHAR | ID do Projeto |
| data_apontamento | DATE | Data do apontamento |
| duracao | INTERVAL | Duração (HH:MM) |
| id_atividade | UUID | FK para atividades |
| comentario | TEXT | Descrição |
| criado_em | TIMESTAMP | Criado em |
| atualizado_em | TIMESTAMP | Atualizado em |

#### Tabela: `atividades`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | UUID | PK |
| nome | VARCHAR | Nome da atividade |
| descricao | TEXT | Descrição |
| ativo | BOOLEAN | Se está ativa |
| criado_por | VARCHAR | ID do usuário que criou |

#### Tabela: `projetos`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | UUID | PK |
| nome | VARCHAR | Nome do projeto |
| descricao | TEXT | Descrição |
| ativo | BOOLEAN | Se está ativo |

#### Tabela: `atividade_projeto`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| atividade_id | UUID | FK para atividades |
| projeto_id | UUID | FK para projetos |

---

## URLs e Domínios

| Ambiente | URL | Uso |
|----------|-----|-----|
| Staging API | https://staging-aponta.treit.com.br/api | Backend |
| Staging Frontend | https://staging-aponta.treit.com.br | Frontend |
| Produção API | https://aponta.treit.com.br/api | Backend |
| Produção Frontend | https://aponta.treit.com.br | Frontend |

---

## Tecnologias

### Backend
- Python 3.12
- FastAPI
- SQLAlchemy 2.0
- Alembic (migrations)
- PyJWT (validação de tokens)
- httpx (cliente HTTP async)

### Frontend
- React 18
- TypeScript
- Vite
- TanStack Query
- Tailwind CSS
- Azure DevOps Extension SDK

### Infraestrutura
- Docker + Docker Compose
- Nginx (proxy reverso + SSL)
- PostgreSQL 15
- VPS Hostinger
