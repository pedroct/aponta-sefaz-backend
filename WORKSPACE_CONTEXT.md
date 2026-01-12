# Contexto do Projeto - API Aponta VPS

## Origem
Projeto criado a partir do `api-aponta-supa` para deploy em VPS Hostinger.

## Repositorio
- **GitHub:** https://github.com/pedroct/api-aponta-vps.git
- **Branch atual:** develop
- **Versao:** v0.1.0

## Estrutura de Branches
```
main     <- Producao (releases com tags)
develop  <- Desenvolvimento (branch atual)
```

## Stack
- **API:** FastAPI (Python 3.12)
- **Banco:** PostgreSQL 15 Alpine
- **Proxy:** Nginx Alpine (portas 80/443)
- **Container:** Docker Compose

## Arquitetura Docker
```
nginx:80/443 -> api:8000 -> postgres:5432
```

## Arquivos Principais
- `docker-compose.yml` - Orquestracao (Nginx + API + PostgreSQL)
- `Dockerfile` - Multi-stage build otimizado
- `nginx/nginx.conf` - Proxy reverso com rate limiting
- `.env.example` - Variaveis de ambiente
- `scripts/deploy.sh` - Script de deploy automatizado
- `.cz.toml` - Commitizen (Conventional Commits + SemVer)

## Versionamento
- **Conventional Commits** para mensagens de commit
- **SemVer** para versionamento
- **Commitizen** configurado (`.cz.toml`)
- **CHANGELOG.md** para historico de mudancas

## Proximos Passos Sugeridos
1. Configurar variaveis de ambiente (.env) na VPS
2. Executar deploy com `./scripts/deploy.sh`
3. Configurar SSL/HTTPS (certificados em nginx/ssl/)
4. Configurar dominio no Nginx

## Comandos Uteis
```bash
# Deploy
./scripts/deploy.sh

# Logs
docker compose logs -f

# Status
docker compose ps

# Commit com Conventional Commits
cz commit

# Bump de versao
cz bump --changelog
```
