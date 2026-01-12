# Certificados SSL

Este diretório está pronto para receber certificados SSL.

## CloudFlare SSL (Recomendado para este projeto)

Como o domínio está configurado no CloudFlare, existem duas opções:

### Opção 1: SSL Flexível (Mais Simples)
No CloudFlare, configure SSL como "Flexible":
- CloudFlare ↔️ Navegador: HTTPS ✅
- CloudFlare ↔️ VPS: HTTP ✅
- **Não precisa de certificado no servidor**
- Configuração atual do Nginx já funciona

### Opção 2: SSL Full (Mais Seguro)
CloudFlare oferece certificado Origin:

1. No CloudFlare Dashboard:
   - SSL/TLS → Origin Server
   - Create Certificate
   - Baixe os arquivos:
     - `origin-cert.pem` (certificado)
     - `origin-key.pem` (chave privada)

2. Copie para este diretório:
   ```bash
   cp origin-cert.pem nginx/ssl/fullchain.pem
   cp origin-key.pem nginx/ssl/privkey.pem
   ```

3. Descomente o bloco HTTPS no `nginx.conf` (linhas 84-96)

4. Reinicie os containers:
   ```bash
   docker compose restart nginx
   ```

## Let's Encrypt (Alternativa)

Se preferir usar Let's Encrypt:

```bash
# Instalar certbot
apt install certbot python3-certbot-nginx

# Gerar certificado
certbot certonly --standalone -d api-aponta.pedroct.com.br

# Certificados ficam em: /etc/letsencrypt/live/api-aponta.pedroct.com.br/
# Copiar para este diretório:
cp /etc/letsencrypt/live/api-aponta.pedroct.com.br/fullchain.pem ./
cp /etc/letsencrypt/live/api-aponta.pedroct.com.br/privkey.pem ./
```

## Status Atual
- ✅ Diretório criado
- ✅ Nginx configurado para usar certificados deste diretório
- ⏳ Aguardando certificados (opcional se usar CloudFlare Flexible)
