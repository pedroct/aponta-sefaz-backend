# Extensão Azure DevOps - Aponta Timetracker

## Visão Geral

Esta extensão adiciona funcionalidades de apontamento de horas ao Azure DevOps.

## Arquivos de Manifesto

| Arquivo | Ambiente | Publisher | URL Base |
|---------|----------|-----------|----------|
| `vss-extension.json` | Produção | `sefaz-ceara` | `https://aponta.treit.com.br` |
| `vss-extension.staging.json` | Staging | `sefaz-ceara-lab` | `https://staging-aponta.treit.com.br` |

## Contribuições da Extensão

### 1. Hub Group "Aponta"
Menu lateral no projeto com as páginas:
- **Timesheet**: Visão semanal de apontamentos
- **Atividades**: Gerenciamento de tipos de atividades

### 2. Work Item Form Group
Painel "Apontamentos" no formulário de Work Items (Tasks/Bugs) para registrar horas diretamente.

## Escopos Necessários

| Escopo | Descrição |
|--------|-----------|
| `vso.profile` | Acesso ao perfil do usuário |
| `vso.work_write` | Leitura e escrita em Work Items |

## Estrutura de Arquivos

```
extension/
├── vss-extension.json           # Manifest produção
├── vss-extension.staging.json   # Manifest staging
├── images/
│   ├── icon-16.png              # Ícone 16x16 (menu)
│   ├── icon-16-dark.png         # Ícone 16x16 (tema escuro)
│   ├── icon-128.png             # Ícone 128x128 (marketplace)
│   └── overview.png             # Screenshot para marketplace
└── dist/                        # Build do frontend (gerado)
    ├── timesheet.html
    ├── atividades.html
    ├── work-item-panel.html
    └── assets/
```

## Como Publicar

### Pré-requisitos

1. **Instalar TFX CLI**:
   ```bash
   npm install -g tfx-cli
   ```

2. **Criar Personal Access Token (PAT)**:
   - Acesse: https://dev.azure.com/{org}/_usersSettings/tokens
   - Scopes necessários: `Marketplace (Publish)`

### Publicação para Staging

```bash
# 1. Build do frontend
cd ../frontend
npm run build

# 2. Copiar dist para extension
cp -r dist ../extension/

# 3. Criar pacote VSIX
cd ../extension
tfx extension create --manifest-globs vss-extension.staging.json

# 4. Publicar (primeira vez)
tfx extension publish --manifest-globs vss-extension.staging.json \
  --token YOUR_PAT \
  --share-with sefaz-ceara-lab

# 4b. Atualizar (versões seguintes)
tfx extension publish --manifest-globs vss-extension.staging.json \
  --token YOUR_PAT
```

### Publicação para Produção

```bash
# 1. Build do frontend (modo produção)
cd ../frontend
npm run build

# 2. Copiar dist para extension
cp -r dist ../extension/

# 3. Atualizar versão no vss-extension.json
# Editar "version": "1.0.1"

# 4. Criar pacote VSIX
cd ../extension
tfx extension create --manifest-globs vss-extension.json

# 5. Publicar
tfx extension publish --manifest-globs vss-extension.json \
  --token YOUR_PAT \
  --share-with sefaz-ceara
```

### Script de Publicação (Automatizado)

```bash
#!/bin/bash
# publish.sh [staging|production]

ENV=${1:-staging}
MANIFEST="vss-extension.json"

if [ "$ENV" == "staging" ]; then
  MANIFEST="vss-extension.staging.json"
  ORG="sefaz-ceara-lab"
else
  ORG="sefaz-ceara"
fi

echo "Publicando para $ENV..."

# Build frontend
cd ../frontend && npm run build

# Copiar dist
cp -r dist ../extension/

# Publicar
cd ../extension
tfx extension publish --manifest-globs $MANIFEST --share-with $ORG

echo "✅ Publicado com sucesso!"
```

## Instalação da Extensão

### No Azure DevOps

1. Acesse: `https://dev.azure.com/{org}/_settings/extensions`
2. Clique em "Shared" (extensões compartilhadas)
3. Encontre "Aponta Timetracker"
4. Clique em "Install"
5. Selecione a organização/projeto

### Verificação

Após instalação:
1. Abra um projeto
2. No menu lateral, deve aparecer "Aponta"
3. Abra um Work Item (Task/Bug), deve aparecer o painel "Apontamentos"

## Troubleshooting

### Extensão não aparece
- Verifique se a extensão foi compartilhada com a organização correta
- Aguarde alguns minutos (cache do Azure DevOps)
- Limpe o cache do navegador

### Erro de CORS
- Verifique se o domínio está correto no `baseUri`
- Verifique configuração do nginx (headers CSP)

### Erro de autenticação
- Verifique se o token do usuário tem os escopos necessários
- Verifique se a API está respondendo

## URLs da API

| Ambiente | Frontend | API |
|----------|----------|-----|
| Produção | `https://aponta.treit.com.br` | `https://aponta.treit.com.br/api/v1` |
| Staging | `https://staging-aponta.treit.com.br` | `https://staging-aponta.treit.com.br/api/v1` |

## Referências

- [Azure DevOps Extension SDK](https://learn.microsoft.com/en-us/azure/devops/extend/overview)
- [Extension Manifest Reference](https://learn.microsoft.com/en-us/azure/devops/extend/develop/manifest)
- [TFX CLI](https://github.com/microsoft/tfs-cli)
