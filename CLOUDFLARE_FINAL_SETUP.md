# Configuração Final CloudFlare - Pronto para Deploy

## ✅ Status: Certificados Instalados e HTTPS Configurado

Data: 2026-01-12
Domínio: **api-aponta.pedroct.com.br**
VPS IP: **31.97.16.12**

---

## 🔐 Certificados SSL Instalados

- ✅ Origin Certificate instalado em `nginx/ssl/fullchain.pem`
- ✅ Private Key instalada em `nginx/ssl/privkey.pem`
- ✅ Permissões configuradas corretamente
- ✅ HTTPS ativado no Nginx (porta 443)

**Domínios cobertos pelo certificado:**
- `api-aponta.pedroct.com.br`
- `*.api-aponta.pedroct.com.br`

**Validade:** 15 anos (até 2041-01-08)

---

## 🎯 Configuração CloudFlare Necessária

### CRÍTICO: Configure no CloudFlare Dashboard

Acesse: https://dash.cloudflare.com/

#### 1. SSL/TLS Mode
**Navegue:** `SSL/TLS` → `Overview`

**Configure para: Full (strict)** ⚠️ IMPORTANTE
```
┌─────────────────────────────────┐
│ ○ Off                           │
│ ○ Flexible                      │
│ ○ Full                          │
│ ● Full (strict)  ← SELECIONE    │
│ ○ Strict (SSL-Only Origin Pull) │
└─────────────────────────────────┘
```

**Porque usar Full (strict):**
- ✅ Criptografia end-to-end (CloudFlare ↔️ VPS)
- ✅ Valida certificado Origin no servidor
- ✅ Máxima segurança

**NÃO use "Flexible":**
- ❌ Conexão CloudFlare → VPS não é criptografada
- ❌ Menos seguro (dados em texto claro entre CF e VPS)

---

#### 2. Always Use HTTPS (Opcional mas Recomendado)
**Navegue:** `SSL/TLS` → `Edge Certificates`

- ✅ Ative: **"Always Use HTTPS"**
  - Redireciona automaticamente HTTP → HTTPS

---

#### 3. Minimum TLS Version
**Navegue:** `SSL/TLS` → `Edge Certificates`

- Selecione: **TLS 1.2** (recomendado)
- Ou: **TLS 1.3** (mais moderno, mas pode ter problemas com clientes antigos)

---

#### 4. HTTP Strict Transport Security (HSTS) - OPCIONAL
**Navegue:** `SSL/TLS` → `Edge Certificates`

⚠️ **CUIDADO:** HSTS força HTTPS permanentemente. Só ative depois de testar tudo.

Se ativar:
- Enable HSTS: ✅
- Max Age: 6 months (padrão)
- Include subdomains: ✅
- Preload: ❌ (deixe desativado inicialmente)

---

## 🚀 Como Fazer o Deploy

### No VPS (31.97.16.12):

```bash
# 1. Conectar no VPS
ssh root@31.97.16.12

# 2. Clonar repositório (se ainda não foi)
cd /opt
git clone https://github.com/pedroct/api-aponta-vps.git
cd api-aponta-vps

# 3. Checkout branch develop
git checkout develop

# 4. Criar arquivo .env
nano .env
# Cole o conteúdo do arquivo .env local (já configurado)

# 5. Executar deploy
./scripts/deploy.sh
```

---

## ✅ Verificações Pós-Deploy

### 1. Health Checks (do VPS)
```bash
# HTTP
curl -v http://localhost/health

# HTTPS (com certificado Origin)
curl -v https://localhost/health -k  # -k ignora validação (certificado é para CloudFlare)
```

### 2. Health Checks Externos (do seu PC)
```bash
# Via CloudFlare (HTTPS)
curl -v https://api-aponta.pedroct.com.br/health

# Verificar SSL/TLS
openssl s_client -connect api-aponta.pedroct.com.br:443 -servername api-aponta.pedroct.com.br
```

### 3. Testes no Navegador
Acesse:
- https://api-aponta.pedroct.com.br/health
- https://api-aponta.pedroct.com.br/docs (Swagger UI)
- https://api-aponta.pedroct.com.br/redoc

Verifique:
- ✅ Cadeado verde no navegador
- ✅ Certificado válido (CloudFlare)
- ✅ Sem erros de certificado

---

## 🔍 Troubleshooting

### Erro: 526 Invalid SSL certificate
**Causa:** CloudFlare configurado em "Full (strict)" mas certificado no servidor inválido

**Solução:**
1. Verifique se os arquivos `fullchain.pem` e `privkey.pem` foram copiados corretamente
2. Reinicie Nginx: `docker compose restart nginx`
3. Verifique logs: `docker compose logs nginx`

### Erro: 525 SSL Handshake Failed
**Causa:** Nginx não conseguiu carregar certificados SSL

**Solução:**
```bash
# Verificar se certificados existem
ls -lh /opt/api-aponta-vps/nginx/ssl/*.pem

# Verificar sintaxe do Nginx
docker exec nginx-aponta nginx -t

# Ver logs detalhados
docker compose logs nginx
```

### Erro: 521 Web Server Is Down
**Causa:** Nginx ou API não estão rodando

**Solução:**
```bash
# Verificar status dos containers
docker compose ps

# Ver logs
docker compose logs -f

# Reiniciar tudo
docker compose restart
```

### HTTP funciona mas HTTPS não
**Causa:** CloudFlare ainda em modo "Flexible" ou certificado não carregado

**Solução:**
1. Verifique modo SSL no CloudFlare: deve estar em **"Full (strict)"**
2. Aguarde 1-2 minutos para propagação
3. Limpe cache do CloudFlare: "Caching" → "Purge Everything"

---

## 📊 Arquitetura Final

```
[Navegador]
    ↓ HTTPS (TLS 1.2/1.3)
[CloudFlare]
    ↓ HTTPS (CloudFlare Origin Certificate)
[VPS: Nginx porta 443]
    ↓ HTTP
[Docker: API porta 8000]
    ↓
[Docker: PostgreSQL porta 5432]
```

**Segurança:**
- ✅ Navegador → CloudFlare: HTTPS público (Let's Encrypt via CF)
- ✅ CloudFlare → VPS: HTTPS privado (Origin Certificate)
- ✅ VPS interno: HTTP (rede Docker isolada)

---

## 📝 Checklist Final

Antes do Deploy:
- ✅ Certificados SSL copiados para `nginx/ssl/`
- ✅ Nginx configurado com HTTPS (porta 443)
- ✅ CloudFlare configurado em **"Full (strict)"**
- ✅ Arquivo `.env` com credenciais corretas
- ✅ DNS apontando para VPS (31.97.16.12)

Após Deploy:
- ⏳ Testar: https://api-aponta.pedroct.com.br/health
- ⏳ Testar: https://api-aponta.pedroct.com.br/docs
- ⏳ Verificar cadeado verde no navegador
- ⏳ Verificar logs: `docker compose logs -f`

---

## 🎉 Próximos Passos

1. **Deploy inicial**
   ```bash
   ssh root@31.97.16.12
   cd /opt/api-aponta-vps
   ./scripts/deploy.sh
   ```

2. **Configurar CloudFlare para Full (strict)**
   - Dashboard → SSL/TLS → Overview → Full (strict)

3. **Testar API**
   - https://api-aponta.pedroct.com.br/docs

4. **Monitoramento** (opcional)
   - Configurar uptime monitoring
   - Configurar alertas de erro

5. **Backups** (opcional)
   - Configurar backup automático do PostgreSQL
   - Script de backup em cron

---

**Tudo pronto para deploy! 🚀**

Quando fizer o deploy, aguarde 30-40 segundos para:
- Migrations do Alembic executarem
- API iniciar completamente
- Health checks passarem

Depois acesse: https://api-aponta.pedroct.com.br/docs
