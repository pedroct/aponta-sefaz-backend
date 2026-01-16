# Instruções de Deploy - API Aponta VPS

## ✅ Status do Projeto: PRONTO PARA DEPLOY

Data: 2026-01-12
Domínio: **api-aponta.pedroct.com.br**
VPS IP: **31.97.16.12** (Hostinger)

---

## Configurações Realizadas

### 1. Arquivos Críticos
- ✅ `.env` configurado com credenciais de produção
- ✅ [nginx/nginx.conf](../../nginx/nginx.conf) - Domínio e CloudFlare configurados
- ✅ [app/main.py](../../app/main.py) - Endpoint `/health` adicionado
- ✅ [app/main.py](../../app/main.py) - CORS usando variável de ambiente
- ✅ Scripts de deploy executáveis

### 2. Banco de Dados
- **Database:** gestao_projetos
- **User:** api-aponta-user
- **Schema:** api_aponta
- **Host:** postgres (container Docker)

### 3. CORS Configurado
```
https://api-aponta.pedroct.com.br
https://*.dev.azure.com
https://*.vsassets.io
https://*.gallerycdn.vsassets.io
```

---

## Como Fazer o Deploy

### Passo 1: Conectar no VPS
```bash
ssh root@31.97.16.12
```

### Passo 2: Clonar o Repositório
```bash
cd /opt
git clone https://github.com/pedroct/api-aponta-vps.git
cd api-aponta-vps
```

### Passo 3: Copiar Arquivo .env
```bash
# Copiar o arquivo .env configurado para o servidor
# Ou criar manualmente com as credenciais corretas
nano .env
```

### Passo 4: Executar Deploy
```bash
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

O script irá:
1. Verificar se `.env` existe
2. Parar containers existentes
3. Construir imagens Docker
4. Iniciar containers (Nginx, API, PostgreSQL)
5. Executar migrations Alembic
6. Verificar health da API

### Passo 5: Verificar Status
```bash
# Ver containers rodando
docker compose ps

# Ver logs em tempo real
docker compose logs -f

# Verificar health
curl http://localhost/health
```

---

## Verificação Pós-Deploy

### 1. Health Checks Locais (no VPS)
```bash
curl http://localhost/health
curl http://localhost/
curl http://localhost/docs
```

### 2. Health Checks Externos (do seu computador)
```bash
curl http://api-aponta.pedroct.com.br/health
curl https://api-aponta.pedroct.com.br/health  # Se CloudFlare SSL ativo
```

### 3. Swagger UI
Acesse no navegador:
- http://api-aponta.pedroct.com.br/docs
- https://api-aponta.pedroct.com.br/docs (com SSL)

---

## CloudFlare SSL

### Opção 1: SSL Flexível (Recomendado inicialmente)
No CloudFlare Dashboard:
1. SSL/TLS → Overview
2. Selecione **"Flexible"**
3. Pronto! HTTPS funcionando

### Opção 2: SSL Full (Mais seguro)
1. No CloudFlare: SSL/TLS → Origin Server
2. Create Certificate
3. Copie certificados para `nginx/ssl/`
4. Descomente bloco HTTPS no `nginx.conf`
5. Reinicie: `docker compose restart nginx`

Veja detalhes em: [nginx/ssl/README.md](../../nginx/ssl/README.md)

---

## Comandos Úteis

```bash
# Ver logs de um serviço específico
docker compose logs -f api
docker compose logs -f nginx
docker compose logs -f postgres

# Reiniciar serviços
docker compose restart api
docker compose restart nginx

# Parar tudo
docker compose down

# Rebuild e restart
docker compose up -d --build

# Ver uso de recursos
docker stats

# Entrar no container da API
docker exec -it api-aponta bash

# Executar migrations manualmente
docker exec -it api-aponta alembic upgrade head
```

---

## Troubleshooting

### Problema: API não inicia
```bash
# Ver logs
docker compose logs api

# Verificar se postgres está rodando
docker compose ps postgres

# Testar conexão com banco
docker exec -it postgres-aponta psql -U api-aponta-user -d gestao_projetos
```

### Problema: Nginx erro 502
```bash
# API ainda está iniciando - aguarde 30-40 segundos
docker compose logs api

# Verificar se API está respondendo
docker exec -it api-aponta curl localhost:8000/health
```

### Problema: Domínio não resolve
```bash
# Verificar DNS no CloudFlare
# Tipo A: api-aponta.pedroct.com.br → 31.97.16.12

# Testar resolução DNS
nslookup api-aponta.pedroct.com.br
dig api-aponta.pedroct.com.br

# Verificar se Nginx está rodando
docker compose ps nginx
curl http://31.97.16.12/health
```

---

## Monitoramento

### Logs em Tempo Real
```bash
docker compose logs -f --tail=100
```

### Verificação Periódica de Health
```bash
# Adicionar ao crontab para monitoramento
*/5 * * * * curl -sf http://localhost/health || echo "API Down!"
```

---

## Próximos Passos (Opcional)

1. **Configurar SSL Full** (CloudFlare Origin Certificate)
2. **Configurar Testes Automatizados** (Pytest)
3. **Configurar CI/CD** (GitHub Actions)
4. **Configurar Backup Automático** do PostgreSQL
5. **Configurar Monitoring** (Prometheus + Grafana)

---

## Informações de Contato

- **GitHub:** https://github.com/pedroct/api-aponta-vps
- **Versão:** v0.1.0
- **Branch:** develop

---

**Pronto para deploy! 🚀**
