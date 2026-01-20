# Ambientes - API Aponta

## Producao

### Servidor VPS (Hostinger)
| Item | Valor |
|------|-------|
| **Host** | srv1264175.hstgr.cloud |
| **IP** | 31.97.16.12 |
| **Acesso SSH** | `ssh root@31.97.16.12` |
| **Caminho do projeto** | /opt/api-aponta-vps |
| **Dominio** | api-aponta.pedroct.com.br |
| **CDN/Proxy** | CloudFlare (SSL/TLS Full Strict) |

### Containers em Producao
| Container | Descricao |
|-----------|-----------|
| api-aponta | API FastAPI |
| postgres-aponta | PostgreSQL 15 |
| nginx-aponta | Nginx proxy reverso |

### Portas em Producao
| Servico | Porta Interna | Porta Externa |
|---------|---------------|---------------|
| API | 8000 | - (via nginx) |
| Nginx | 80, 443 | 80, 443 |
| PostgreSQL | 5432 | 5432 |

---

## Desenvolvimento Local

### Containers Docker
| Container | Descricao |
|-----------|-----------|
| api-aponta-local | API FastAPI (porta 8000) |
| postgres-aponta | PostgreSQL 15 compartilhado |

### Rede Docker
- **Nome:** api-aponta_aponta-network
- **Driver:** bridge

### URLs de Desenvolvimento
| Servico | URL |
|---------|-----|
| API | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| Health Check | http://localhost:8000/ |

### Banco de Dados
| Item | Valor |
|------|-------|
| **Host (dentro do container)** | postgres-aponta |
| **Host (fora do container)** | localhost |
| **Porta** | 5432 |
| **Database** | gestao_projetos |
| **Schema** | api_aponta |
| **Usuario** | aponta_user |

> **Nota:** O container postgres-aponta e compartilhado com outras aplicacoes, nao e dedicado exclusivamente ao api-aponta.

### Comandos Uteis

#### Iniciar ambiente de desenvolvimento
```bash
# Iniciar containers
docker start postgres-aponta api-aponta-local

# Verificar status
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Ver logs da API
docker logs -f api-aponta-local
```

#### Reconstruir imagem da API
```bash
cd /home/pedroctdev/apps/api-aponta-vps

# Build da imagem
docker build -t api-aponta:latest .

# Recriar container
docker rm -f api-aponta-local
docker run -d \
  --name api-aponta-local \
  --network api-aponta_aponta-network \
  -p 8000:8000 \
  --env-file .env \
  -e DATABASE_HOST=postgres-aponta \
  -e "DATABASE_URL=postgresql://aponta_user:aponta_secret_password@postgres-aponta:5432/gestao_projetos" \
  api-aponta:latest
```

#### Executar migrations
```bash
docker exec -it api-aponta-local alembic upgrade head
```

---

## Variaveis de Ambiente

### Desenvolvimento (.env)
```env
DATABASE_NAME=gestao_projetos
DATABASE_USER=aponta_user
DATABASE_PASSWORD=aponta_secret_password
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_SCHEMA=api_aponta
DATABASE_URL=postgresql://aponta_user:aponta_secret_password@localhost:5432/gestao_projetos

AZURE_DEVOPS_ORG_URL=https://dev.azure.com/sefaz-ceara-lab
ENVIRONMENT=development
API_DEBUG=true
```

### Producao
As variaveis de producao estao configuradas no arquivo `.env` do servidor VPS em `/opt/api-aponta-vps/.env`.

---

## CI/CD

### GitHub Actions
- **Workflow:** `.github/workflows/deploy.yml`
- **Trigger:** Push para branch `develop` ou `main`
- **Deploy automatico:** Sim (apos testes passarem)

### Secrets do GitHub
| Secret | Descricao |
|--------|-----------|
| VPS_HOST | 31.97.16.12 |
| VPS_USER | root |
| VPS_PATH | /opt/api-aponta-vps |
| VPS_SSH_PRIVATE_KEY | Chave privada SSH |

---

**Ultima atualizacao:** 2026-01-18
