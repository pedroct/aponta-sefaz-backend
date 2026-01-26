# Índice da Documentação - Sistema Aponta

**Última atualização:** 21/01/2026

---

## Documentos nesta pasta

| Arquivo | Descrição |
|---------|-----------|
| [AUTENTICACAO.md](AUTENTICACAO.md) | Fluxo de autenticação com App Token JWT e PAT |
| [ARQUITETURA.md](ARQUITETURA.md) | Visão geral da arquitetura e componentes |
| [DEPLOY.md](DEPLOY.md) | Comandos de deploy e operações no VPS |

---

## Resumo Rápido

### ⚠️ Regra de Ouro da Autenticação
- **App Token JWT** → Apenas para identificar o usuário (não chama APIs do Azure)
- **PAT do backend** → Para todas as chamadas à API do Azure DevOps (WIQL, Work Items, etc.)

### Schemas do Banco de Dados
| Ambiente | Schema |
|----------|--------|
| Staging | `aponta_sefaz_staging` |
| Produção | `aponta_sefaz` |

### Componentes
- **Backend**: FastAPI + SQLAlchemy + PostgreSQL
- **Frontend**: React + Vite + TypeScript
- **Extensão**: timesheet.html (iframe para React app)

### URLs
| Ambiente | URL |
|----------|-----|
| Staging | https://staging-aponta.treit.com.br |
| Produção | https://aponta.treit.com.br |

### VPS
- IP: 92.112.178.252
- Acesso: `ssh root@92.112.178.252`

### Containers
| Container | Ambiente | Porta |
|-----------|----------|-------|
| api-aponta-staging | Staging | 8001 |
| api-aponta-prod | Produção | 8000 |
| postgres-aponta | Banco | 5432 |

### Arquivos de Ambiente
- Staging: `/root/staging.env`
- Produção: `/root/prod.env`
