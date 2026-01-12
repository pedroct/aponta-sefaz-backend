# Configuração de Deployment - GitHub Actions

Este documento explica como configurar os **GitHub Secrets** necessários para a pipeline de CI/CD automatizada.

## 📋 Secrets Necessários

A pipeline requer 4 secrets configurados no repositório:

| Secret | Descrição | Exemplo |
|--------|-----------|---------|
| `VPS_HOST` | IP ou hostname do servidor VPS | `31.97.16.12` |
| `VPS_USER` | Usuário SSH do servidor | `root` |
| `VPS_PATH` | Caminho do projeto no servidor | `/opt/api-aponta-vps` |
| `VPS_SSH_PRIVATE_KEY` | Chave privada SSH completa | Conteúdo do arquivo `~/.ssh/id_rsa` |

---

## 🔧 Como Configurar os Secrets

### Opção 1: Interface Web do GitHub

1. Acesse o repositório: https://github.com/pedroct/api-aponta-vps
2. Vá para **Settings** → **Secrets and variables** → **Actions**
3. Clique em **New repository secret**
4. Adicione cada secret:

#### VPS_HOST
- **Name**: `VPS_HOST`
- **Value**: `31.97.16.12`

#### VPS_USER
- **Name**: `VPS_USER`
- **Value**: `root`

#### VPS_PATH
- **Name**: `VPS_PATH`
- **Value**: `/opt/api-aponta-vps`

#### VPS_SSH_PRIVATE_KEY
- **Name**: `VPS_SSH_PRIVATE_KEY`
- **Value**: Cole o conteúdo completo da sua chave privada SSH

**Como obter a chave privada SSH:**

```bash
# No seu computador local, exiba a chave privada:
cat ~/.ssh/id_rsa

# Ou, se estiver usando uma chave específica:
cat ~/.ssh/id_ed25519

# Copie TODO o conteúdo, incluindo as linhas:
# -----BEGIN OPENSSH PRIVATE KEY-----
# ... (conteúdo da chave)
# -----END OPENSSH PRIVATE KEY-----
```

⚠️ **IMPORTANTE**: A chave privada deve:
- Incluir as linhas BEGIN e END
- Não ter senha/passphrase (ou você precisará configurar ssh-agent com passphrase)
- Ter permissão de acesso ao servidor VPS

---

### Opção 2: GitHub CLI (gh)

Se você tem o GitHub CLI instalado:

```bash
# Configurar VPS_HOST
gh secret set VPS_HOST --body "31.97.16.12" -R pedroct/api-aponta-vps

# Configurar VPS_USER
gh secret set VPS_USER --body "root" -R pedroct/api-aponta-vps

# Configurar VPS_PATH
gh secret set VPS_PATH --body "/opt/api-aponta-vps" -R pedroct/api-aponta-vps

# Configurar VPS_SSH_PRIVATE_KEY (lê do arquivo)
gh secret set VPS_SSH_PRIVATE_KEY --body "$(cat ~/.ssh/id_rsa)" -R pedroct/api-aponta-vps
```

---

## ✅ Verificação

Após configurar os secrets:

1. Acesse: https://github.com/pedroct/api-aponta-vps/actions
2. Clique em **Actions** → **Deploy to VPS**
3. Clique em **Run workflow** → **Run workflow** (ou faça um push para `develop`)
4. Acompanhe a execução

A pipeline agora deve:
- ✅ Validar que todos os secrets estão configurados
- ✅ Executar os testes
- ✅ Fazer deploy no VPS
- ✅ Verificar o health check

---

## 🔐 Segurança da Chave SSH

### Gerar uma nova chave SSH (se necessário)

Se você não tem uma chave SSH ou quer criar uma específica para o deploy:

```bash
# Gerar nova chave SSH (sem senha para automação)
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/github_actions_deploy -N ""

# Copiar a chave pública para o servidor
ssh-copy-id -i ~/.ssh/github_actions_deploy.pub root@31.97.16.12

# Testar a conexão
ssh -i ~/.ssh/github_actions_deploy root@31.97.16.12 "echo 'Conexão OK'"

# Usar essa chave no secret VPS_SSH_PRIVATE_KEY
cat ~/.ssh/github_actions_deploy
```

### Verificar acesso SSH no servidor

A chave pública deve estar em:

```bash
# No servidor VPS
cat /root/.ssh/authorized_keys
# Deve conter a chave pública correspondente à chave privada configurada no GitHub
```

---

## 🐛 Troubleshooting

### Erro: "VPS_HOST secret is not set"
- Verifique se o secret foi criado com o nome exato: `VPS_HOST` (case-sensitive)
- Verifique se está no nível de repositório, não de ambiente

### Erro: "Permission denied (publickey)"
- A chave privada configurada não corresponde a nenhuma chave autorizada no servidor
- Execute `ssh-copy-id` para adicionar a chave pública ao servidor
- Verifique `/root/.ssh/authorized_keys` no servidor

### Erro: "The 'file' argument must be of type string"
- O secret `VPS_SSH_PRIVATE_KEY` está vazio ou mal formatado
- Certifique-se de copiar TODO o conteúdo da chave, incluindo BEGIN/END

### Pipeline falha no health check
- Verifique se o arquivo `.env` existe no servidor: `/opt/api-aponta-vps/.env`
- Verifique se os certificados SSL existem: `/opt/api-aponta-vps/nginx/ssl/`
- Verifique os logs: `docker compose logs -f api`

---

## 📚 Referências

- [GitHub Actions Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [SSH Key Authentication](https://www.ssh.com/academy/ssh/key)
- [Workflow Deploy](.github/workflows/deploy.yml)