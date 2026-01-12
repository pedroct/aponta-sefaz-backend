# Guia: Copiar Arquivos para o VPS

## 📋 Arquivos que Precisam Ser Copiados

### Obrigatórios
- `.env` - Credenciais e configurações (200 KB)
- `nginx/ssl/fullchain.pem` - Certificado SSL (2 KB)
- `nginx/ssl/privkey.pem` - Chave privada SSL (2 KB)

**Total:** ~204 KB

---

## 🚀 Método 1: SCP (Recomendado)

### Windows (Git Bash / WSL)

```bash
# No diretório do projeto local
cd /home/pedroctdev/apps/api-aponta-vps

# 1. Copiar .env
scp .env root@31.97.16.12:/opt/api-aponta-vps/.env

# 2. Copiar certificados
scp nginx/ssl/fullchain.pem root@31.97.16.12:/opt/api-aponta-vps/nginx/ssl/
scp nginx/ssl/privkey.pem root@31.97.16.12:/opt/api-aponta-vps/nginx/ssl/

# Verificar
ssh root@31.97.16.12 "ls -lh /opt/api-aponta-vps/.env /opt/api-aponta-vps/nginx/ssl/*.pem"
```

---

## 📝 Método 2: Copiar e Colar Manual

### Passo 1: Conectar no VPS

```bash
ssh root@31.97.16.12
cd /opt/api-aponta-vps
```

### Passo 2: Criar .env

```bash
nano .env
```

**No seu computador:**
1. Abra: `.env`
2. Copie TUDO (Ctrl+A, Ctrl+C)

**No VPS (nano):**
1. Cole o conteúdo (Ctrl+Shift+V ou botão direito)
2. Salve: `Ctrl+X` → `Y` → `Enter`

### Passo 3: Criar fullchain.pem

```bash
nano nginx/ssl/fullchain.pem
```

**No seu computador:**
1. Abra: `nginx/ssl/fullchain.pem`
2. Copie TUDO (começando com `-----BEGIN CERTIFICATE-----`)

**No VPS (nano):**
1. Cole o conteúdo
2. Salve: `Ctrl+X` → `Y` → `Enter`

### Passo 4: Criar privkey.pem

```bash
nano nginx/ssl/privkey.pem
```

**No seu computador:**
1. Abra: `nginx/ssl/privkey.pem`
2. Copie TUDO (começando com `-----BEGIN PRIVATE KEY-----`)

**No VPS (nano):**
1. Cole o conteúdo
2. Salve: `Ctrl+X` → `Y` → `Enter`

### Passo 5: Verificar

```bash
# Verificar se arquivos existem
ls -lh .env nginx/ssl/*.pem

# Verificar conteúdo (primeiras linhas)
head -5 .env
head -5 nginx/ssl/fullchain.pem
head -5 nginx/ssl/privkey.pem
```

**Output esperado:**
```
-rw-r--r-- 1 root root 1.1K Jan 12 10:00 .env
-rw-r--r-- 1 root root 1.7K Jan 12 10:01 nginx/ssl/fullchain.pem
-rw-r--r-- 1 root root 1.7K Jan 12 10:02 nginx/ssl/privkey.pem
```

---

## 🔒 Método 3: SFTP (GUI)

### Usando FileZilla / WinSCP

1. **Conectar:**
   - Host: `31.97.16.12`
   - Port: `22`
   - Protocol: `SFTP`
   - User: `root`
   - Password: (sua senha)

2. **Navegar:**
   - Remote: `/opt/api-aponta-vps`

3. **Arrastar e soltar:**
   - Local `.env` → Remote `/opt/api-aponta-vps/`
   - Local `nginx/ssl/fullchain.pem` → Remote `/opt/api-aponta-vps/nginx/ssl/`
   - Local `nginx/ssl/privkey.pem` → Remote `/opt/api-aponta-vps/nginx/ssl/`

---

## ✅ Verificação Final

Execute no VPS:

```bash
cd /opt/api-aponta-vps

# 1. Arquivo .env existe e tem conteúdo
test -f .env && echo "✓ .env OK" || echo "✗ .env FALTANDO"
grep -q "DATABASE_NAME" .env && echo "✓ .env tem conteúdo" || echo "✗ .env vazio"

# 2. Certificados existem
test -f nginx/ssl/fullchain.pem && echo "✓ fullchain.pem OK" || echo "✗ fullchain.pem FALTANDO"
test -f nginx/ssl/privkey.pem && echo "✓ privkey.pem OK" || echo "✗ privkey.pem FALTANDO"

# 3. Certificados têm formato correto
grep -q "BEGIN CERTIFICATE" nginx/ssl/fullchain.pem && echo "✓ fullchain.pem válido" || echo "✗ fullchain.pem inválido"
grep -q "BEGIN PRIVATE KEY" nginx/ssl/privkey.pem && echo "✓ privkey.pem válido" || echo "✗ privkey.pem inválido"
```

**Output esperado:**
```
✓ .env OK
✓ .env tem conteúdo
✓ fullchain.pem OK
✓ privkey.pem OK
✓ fullchain.pem válido
✓ privkey.pem válido
```

---

## 🎯 Próximo Passo

Depois de copiar os arquivos, execute o deploy:

```bash
chmod +x QUICK_DEPLOY.sh
./QUICK_DEPLOY.sh
```

Ou use o script original:

```bash
./scripts/deploy.sh
```

---

## ⚠️ Troubleshooting

### Erro: "Permission denied"
```bash
# Dar permissão ao usuário root
chmod 600 .env
chmod 644 nginx/ssl/fullchain.pem
chmod 600 nginx/ssl/privkey.pem
```

### Erro: "No such file or directory"
```bash
# Criar diretórios se não existirem
mkdir -p nginx/ssl
```

### Certificado não funciona
```bash
# Verificar formato
cat nginx/ssl/fullchain.pem | head -1
# Deve mostrar: -----BEGIN CERTIFICATE-----

cat nginx/ssl/privkey.pem | head -1
# Deve mostrar: -----BEGIN PRIVATE KEY-----
```

### .env com caracteres estranhos
```bash
# Remover BOM (Byte Order Mark) se existir
sed -i '1s/^\xEF\xBB\xBF//' .env

# Converter line endings
dos2unix .env  # Se dos2unix estiver instalado
```

---

## 📞 Precisa de Ajuda?

Se encontrar problemas:
1. Verifique os logs: `docker compose logs -f`
2. Consulte: [DEPLOY_INSTRUCTIONS.md](DEPLOY_INSTRUCTIONS.md)
3. Troubleshooting: [CLOUDFLARE_FINAL_SETUP.md](CLOUDFLARE_FINAL_SETUP.md)
