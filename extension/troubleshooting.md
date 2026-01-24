# Troubleshooting - Extensão Azure DevOps

## Problemas Identificados e Soluções

### 1. Erro "VSS is not defined"
**Causa**: O SDK do Azure DevOps não está carregando corretamente.

**Solução**:
- Verificar se o arquivo `dist/` existe na extensão
- Garantir que os arquivos HTML referenciem corretamente o VSS SDK
- Usar URL do CDN oficial: `https://almsaasscus.vsassets.io/v1.2021.0607.1/VSS.SDK.min.js`

### 2. Content Security Policy (CSP) Violations
**Causa**: Recursos da Microsoft sendo bloqueados pela política de segurança.

**Soluções**:
- Configurar CORS no backend para incluir domínios Azure DevOps
- Verificar se adblockers estão bloqueando recursos
- Testar em modo incógnito do navegador

### 3. NET::ERR_BLOCKED_BY_CLIENT
**Causa**: Extensões do navegador (adblockers) bloqueando requests.

**Soluções**:
- Desabilitar adblockers temporariamente
- Adicionar exceções para domínios Azure DevOps
- Testar em modo incógnito

### 4. NET::ERR_NAME_NOT_RESOLVED para vsassets.io
**Causa**: Problemas de conectividade ou bloqueios de rede.

**Soluções**:
- Verificar conectividade com internet
- Testar acesso direto: https://vsassets.io
- Verificar configurações de proxy/firewall

## Domínios que devem estar liberados:

```
- https://dev.azure.com
- https://vsassets.io  
- https://almsaasscus.vsassets.io
- https://sefaz-ceara.gallerycdn.vsassets.io
- https://sefaz-ceara-lab.gallerycdn.vsassets.io
- https://amcdn.msftauth.net
- https://js.monitor.azure.com
- https://browser.events.data.microsoft.com
```

## Verificações para Debug:

1. **Console do navegador**: Verificar se há erros de carregamento
2. **Network tab**: Verificar se requests estão sendo bloqueados
3. **Modo incógnito**: Testar sem extensões/adblockers
4. **CORS**: Verificar se backend permite origens Azure DevOps
5. **Extension manifest**: Verificar se paths estão corretos

## Status atual:
- ✅ CORS configurado no backend (.env atualizado)
- ⚠️  Extensão precisa ser testada sem adblockers
- ⚠️  Verificar se arquivos dist/ existem