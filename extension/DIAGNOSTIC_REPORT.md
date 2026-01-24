# 🚨 DIAGNÓSTICO COMPLETO: Problemas da Extensão Azure DevOps

## 📊 Status Atual (Atualizado: 24/01/2026)

### ✅ O que está funcionando:
- 🟢 Backend API funcionando (https://aponta.treit.com.br/health)
- 🟢 CORS configurado corretamente
- 🟢 Conexão SSH com VPS funcionando
- 🟢 Containers staging rodando normalmente
- 🟢 DNS resolução funciona com Google DNS (8.8.8.8)

### ❌ O que está com problema:
- 🔴 **vsassets.io não acessível** (IP 191.238.172.191 bloqueado)
- 🔴 **Microsoft VSS Web Extension SDK arquivado** (desde 27/01/2023)
- 🔴 Diretório `dist/` não existe na extensão
- 🔴 Arquivos HTML da extensão não encontrados

## 🔍 Causa Raiz Identificada

### 1. Problema de Conectividade
```
Test-NetConnection vsassets.io -Port 443
❌ TcpTestSucceeded : False
❌ PingSucceeded    : False
```

### 2. SDK Descontinuado
O repositório [microsoft/vss-web-extension-sdk](https://github.com/microsoft/vss-web-extension-sdk) foi:
- ❌ **Arquivado em 27 de janeiro de 2023**
- ❌ **Read-only** (não aceita mais issues/PRs)
- ❌ Muitas issues abertas não resolvidas (#164: "VSS is not defined")

### 3. Arquivos de Build Ausentes
```
ls extension/dist/
ERROR: no such file or directory
```

## 🛠️ SOLUÇÕES IMPLEMENTADAS

### ✅ 1. CORS Atualizado
Arquivo `.env` atualizado com todos os domínios necessários:
```env
CORS_ORIGINS=...,https://dev.azure.com,https://vsassets.io,https://almsaasscus.vsassets.io,...
```

### ✅ 2. Script de Diagnóstico
Criado `extension/test-connectivity.sh` para debugging

### ✅ 3. Documentação de Troubleshooting  
Criado `extension/troubleshooting.md` com soluções

## 🎯 PRÓXIMOS PASSOS RECOMENDADOS

### 📋 1. Solução Imediata (Rede)
```powershell
# Testar sem adblockers
Start-Process msedge -ArgumentList "--incognito https://dev.azure.com"

# Configurar DNS alternativo
netsh interface ip set dns "Ethernet" static 8.8.8.8
netsh interface ip add dns "Ethernet" 8.8.4.4 index=2
```

### 📋 2. Solução de Build (Extensão)
```bash
# Verificar se existe projeto frontend
find . -name "package.json" -o -name "vite.config.js" -o -name "webpack.config.js"

# Se encontrado, fazer build:
npm install
npm run build
```

### 📋 3. Solução Alternativa (CDN)
Se vsassets.io continuar inacessível, usar CDNs alternativos:
- jsdelivr: `https://cdn.jsdelivr.net/npm/vss-web-extension-sdk@5.141.0/lib/VSS.SDK.min.js`
- unpkg: `https://unpkg.com/vss-web-extension-sdk@5.141.0/lib/VSS.SDK.min.js`

### 📋 4. Solução Definitiva (Local)
Hospedar o VSS.SDK.min.js localmente:
```bash
# Download manual
wget https://almsaasscus.vsassets.io/v1.2021.0607.1/VSS.SDK.min.js
# Incluir no manifest como arquivo local
```

## 📞 CONTATO PARA SUPORTE
Se os problemas persistirem:

1. **Verificar firewall/proxy corporativo**
2. **Testar em rede diferente** 
3. **Contatar administrador de rede** sobre bloqueios do IP 191.238.172.191
4. **Considerar usar VPN** para contornar bloqueios

---

**⚠️ IMPORTANTE:** O SDK oficial da Microsoft foi descontinuado. Considere migrar para as novas APIs do Azure DevOps quando possível.