#!/bin/bash

# Script para testar conectividade com domínios Azure DevOps

echo "🔄 Testando conectividade com domínios Azure DevOps..."
echo "============================================="

domains=(
    "https://dev.azure.com"
    "https://vsassets.io"
    "https://almsaasscus.vsassets.io"
    "https://amcdn.msftauth.net"
    "https://js.monitor.azure.com"
    "https://browser.events.data.microsoft.com"
    "https://aponta.treit.com.br"
)

for domain in "${domains[@]}"; do
    echo -n "Testing $domain ... "
    if curl -s --connect-timeout 5 --max-time 10 "$domain" > /dev/null 2>&1; then
        echo "✅ OK"
    else
        echo "❌ FAILED"
    fi
done

echo ""
echo "🔧 Testando CORS da API:"
echo "============================================="

cors_test_origins=(
    "https://dev.azure.com"
    "https://vsassets.io" 
    "https://sefaz-ceara.gallerycdn.vsassets.io"
)

for origin in "${cors_test_origins[@]}"; do
    echo -n "Testing CORS for $origin ... "
    response=$(curl -s -H "Origin: $origin" -H "Access-Control-Request-Method: GET" -X OPTIONS https://aponta.treit.com.br/api/v1/projetos)
    if [[ "$response" == "OK" ]]; then
        echo "✅ OK"
    else
        echo "❌ FAILED"
    fi
done

echo ""
echo "📋 Resumo:"
echo "============================================="
echo "Se todos os testes passaram, o problema pode ser:"
echo "1. 🚫 Adblocker bloqueando recursos"
echo "2. 🏢 Proxy/Firewall corporativo"
echo "3. 📁 Arquivos da extensão não encontrados (dist/ missing)"
echo "4. 🔧 Configuração do manifesto da extensão"
echo ""
echo "💡 Soluções recomendadas:"
echo "- Testar em modo incógnito do navegador"
echo "- Desabilitar temporariamente adblockers"
echo "- Verificar se o diretório dist/ existe na extensão"
echo "- Verificar console do navegador para erros específicos"