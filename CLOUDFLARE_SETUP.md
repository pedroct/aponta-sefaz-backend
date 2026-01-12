# Configuração CloudFlare - API Aponta

## Informações do Domínio
- **Domínio:** api-aponta.pedroct.com.br
- **VPS IP:** 31.97.16.12 (Hostinger)
- **Proxy:** CloudFlare (laranja ativado)

---

## Configurações DNS no CloudFlare

### Registro A (Principal)
```
Type: A
Name: api-aponta
Content: 31.97.16.12
Proxy: ✅ Proxied (laranja)
TTL: Auto
```

### Verificação
```bash
# Testar resolução DNS
nslookup api-aponta.pedroct.com.br

# Deve retornar IPs do CloudFlare (não o IP do VPS diretamente)
```

---

## SSL/TLS Configuration

### Opção 1: Flexible (Início Rápido) ⚡
**Recomendado para começar**

**No CloudFlare Dashboard:**
1. Vá em: `SSL/TLS` → `Overview`
2. Selecione: **"Flexible"**

**Como funciona:**
```
[Navegador] --HTTPS--> [CloudFlare] --HTTP--> [VPS]
```

**Vantagens:**
- ✅ Configuração imediata
- ✅ Não precisa configurar certificado no servidor
- ✅ Usuários acessam via HTTPS
- ✅ Configuração atual do Nginx já funciona

**Desvantagens:**
- ⚠️ Conexão CloudFlare → VPS não é criptografada

---

### Opção 2: Full (Strict) - Segurança Máxima 🔒
**Recomendado para produção**

**No CloudFlare Dashboard:**
1. Vá em: `SSL/TLS` → `Overview`
2. Selecione: **"Full (strict)"**
3. Vá em: `SSL/TLS` → `Origin Server`
4. Clique em: **"Create Certificate"**

**Configurações do Certificado:**
- Private key type: `RSA (2048)`
- Hostnames: `api-aponta.pedroct.com.br, *.api-aponta.pedroct.com.br`
- Certificate Validity: `15 years`

**Download:**
- Salve o **Origin Certificate** como `origin-cert.pem`
- Salve o **Private Key** como `origin-key.pem`

**No VPS:**
```bash
# 1. Copie os certificados para o diretório SSL
cd /opt/api-aponta-vps
nano nginx/ssl/fullchain.pem  # Cole o conteúdo de origin-cert.pem
nano nginx/ssl/privkey.pem    # Cole o conteúdo de origin-key.pem

# 2. Ajuste permissões
chmod 644 nginx/ssl/fullchain.pem
chmod 600 nginx/ssl/privkey.pem

# 3. Edite o nginx.conf
nano nginx/nginx.conf

# 4. Descomente o bloco HTTPS (linhas 84-96)
# E altere o server_name para: api-aponta.pedroct.com.br

# 5. Reinicie o Nginx
docker compose restart nginx

# 6. Verifique os logs
docker compose logs nginx
```

**Como funciona:**
```
[Navegador] --HTTPS--> [CloudFlare] --HTTPS--> [VPS]
```

**Vantagens:**
- ✅ Criptografia end-to-end
- ✅ Máxima segurança
- ✅ Validação de certificado

---

## Outras Configurações Recomendadas

### 1. Always Use HTTPS
**SSL/TLS → Edge Certificates**
- ✅ Ative: "Always Use HTTPS"
- Redireciona automaticamente HTTP → HTTPS

### 2. HTTP Strict Transport Security (HSTS)
**SSL/TLS → Edge Certificates**
- ✅ Ative: "Enable HSTS"
- Max Age: 12 meses
- ✅ Include subdomains
- ✅ Preload

### 3. Minimum TLS Version
**SSL/TLS → Edge Certificates**
- Selecione: **TLS 1.2** (mínimo recomendado)

### 4. Opportunistic Encryption
**SSL/TLS → Edge Certificates**
- ✅ Ative: "Opportunistic Encryption"

### 5. TLS 1.3
**SSL/TLS → Edge Certificates**
- ✅ Ative: "TLS 1.3"

---

## Firewall Rules (Opcional)

### Proteger Endpoints Sensíveis
**Security → WAF → Custom rules**

**Regra: Rate Limiting Global**
```
(http.host eq "api-aponta.pedroct.com.br")
Action: Challenge
Rate: 100 requests per 1 minute
```

**Regra: Bloquear países específicos (exemplo)**
```
(http.host eq "api-aponta.pedroct.com.br" and ip.geoip.country in {"CN" "RU"})
Action: Block
```

---

## Page Rules (Otimização)

**Rules → Page Rules**

### Rule 1: API Cache (se aplicável)
```
URL: api-aponta.pedroct.com.br/api/*
Settings:
  - Cache Level: Standard
  - Edge Cache TTL: 2 hours
```

---

## Verificação Final

### Teste SSL
```bash
# Testar SSL/TLS
curl -I https://api-aponta.pedroct.com.br/health

# Verificar certificado
openssl s_client -connect api-aponta.pedroct.com.br:443 -servername api-aponta.pedroct.com.br

# Teste online
https://www.ssllabs.com/ssltest/analyze.html?d=api-aponta.pedroct.com.br
```

### Health Checks
```bash
# HTTP (se Flexible)
curl http://api-aponta.pedroct.com.br/health

# HTTPS (sempre)
curl https://api-aponta.pedroct.com.br/health

# Docs
https://api-aponta.pedroct.com.br/docs
```

---

## Timeline de Propagação

- **DNS Changes:** 5-10 minutos (com CloudFlare)
- **SSL Certificate:** Instantâneo (após configuração)
- **Cache Purge:** Use "Purge Everything" se necessário

---

## Troubleshooting

### Erro: ERR_SSL_VERSION_OR_CIPHER_MISMATCH
- Verifique se escolheu "Full (strict)" mas não instalou certificado
- Mude para "Flexible" ou instale certificado Origin

### Erro: 502 Bad Gateway
- API ainda está iniciando (aguarde 30s)
- Verifique: `docker compose logs api`

### Erro: 522 Connection Timed Out
- Firewall do VPS bloqueando CloudFlare
- Verifique: `ufw status` e libere portas 80/443

### Erro: 525 SSL Handshake Failed
- Certificado no servidor está inválido ou expirado
- Use certificado CloudFlare Origin (válido por 15 anos)

---

## Status Atual

- ✅ DNS configurado e apontando para VPS
- ✅ Nginx configurado com IPs do CloudFlare
- ✅ Headers CF-Connecting-IP configurados
- ⏳ SSL: Aguardando escolha (Flexible ou Full)

---

## Próximo Passo

**Escolha uma opção:**

1. **SSL Flexible (Rápido):** Apenas ative no CloudFlare
2. **SSL Full (Seguro):** Gere certificado Origin e configure no Nginx

---

**Depois do deploy, acesse:**
- 📡 https://api-aponta.pedroct.com.br/health
- 📚 https://api-aponta.pedroct.com.br/docs
