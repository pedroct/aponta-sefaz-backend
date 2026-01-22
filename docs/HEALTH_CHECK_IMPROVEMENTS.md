# Health Check Improvements

## Overview

Implementamos melhorias significativas nos scripts de deploy para tornar o health check mais robusto e confiável. As mudanças resolvem o problema de timing que causava falsos negativos durante a inicialização da API.

## Problemas Resolvidos

### 1. **Timing Issues**
- **Antes**: Sleep fixo de 30-40 segundos sem validação real
- **Depois**: Retry logic que aguarda efetivamente a API estar pronta

### 2. **False Negatives**
- **Antes**: Falhas no health check mesmo com API funcionando
- **Depois**: Múltiplas tentativas garantem que a API tenha tempo suficiente para inicializar

### 3. **Timeouts não informativos**
- **Antes**: Não havia indicação clara se a falha era temporária ou real
- **Depois**: Feedback detalhado em cada tentativa com recomendações

## Implementação

### Retry Logic com 5 Tentativas

```bash
max_attempts=5
attempt=1
health_ok=false

while [ $attempt -le $max_attempts ]; do
    echo -n "  [Tentativa $attempt/$max_attempts] "
    
    if curl -sf --connect-timeout 5 --max-time 10 http://localhost/health > /dev/null 2>&1; then
        echo "✅"
        health_ok=true
        break
    else
        echo "⏳"
        if [ $attempt -lt $max_attempts ]; then
            sleep 8  # 8 segundos entre tentativas
        fi
    fi
    
    attempt=$((attempt + 1))
done
```

### Melhorias de curl

- `--connect-timeout 5`: Timeout de conexão de 5 segundos
- `--max-time 10`: Timeout máximo de 10 segundos por tentativa
- Output silencioso com `-s` e falha com `-f`

### Timeouts Totais

- **Mínimo**: ~5 segundos (1ª tentativa bem-sucedida)
- **Máximo**: ~40 segundos (5 tentativas × 8 segundos)

Esta é a duração típica necessária para uma inicialização completa do FastAPI com Alembic.

## Arquivos Modificados

### 1. **manual_deploy.sh**
- ✅ Retry logic implementada
- ✅ Timeouts otimizados
- ✅ Mensagens de feedback detalhadas

### 2. **QUICK_DEPLOY.sh**
- ✅ Retry logic implementada
- ✅ Tratamento de falha sem abortar deploy
- ✅ Troubleshooting expandido

### 3. **deploy.sh**
- ✅ Retry logic integrada na função deploy_env
- ✅ Health check remoto com retry
- ✅ Melhor tratamento de erros

## Uso

### Manual Deploy
```bash
./manual_deploy.sh
```

Saída esperada:
```
🏥 Testando health check com retry logic:
  [Tentativa 1/5] Verificando saúde da API... ⏳
  [Tentativa 2/5] Verificando saúde da API... ⏳
  [Tentativa 3/5] Verificando saúde da API... ✅
  
✅ Health check passou! API está pronta para uso.
```

### Quick Deploy
```bash
./QUICK_DEPLOY.sh
```

### Regular Deploy
```bash
./deploy.sh staging
./deploy.sh production
./deploy.sh all
```

## Saída Detalhada

### Sucesso
```
✅ Health check passou! API está pronta para uso.
```

### Falha com Recomendações
```
⚠️  Timeout no health check após 5 tentativas.
Os containers estão rodando, mas a API pode ainda estar inicializando.
Recomendações:
  1. Verifique os logs: docker compose logs -f api
  2. Aguarde mais 10-15 segundos e teste novamente
  3. Se o problema persistir, verifique: docker compose logs --tail=50 api
```

## Debugging

Se o health check continuar falhando, execute:

```bash
# Verificar logs em tempo real
docker compose logs -f api

# Últimas 50 linhas de log
docker compose logs --tail=50 api

# Status dos containers
docker compose ps

# Testar manualmente
curl http://localhost/health
curl http://localhost/api/v1
```

## Configuração

Para ajustar o comportamento, edite os scripts:

### Aumentar tentativas
```bash
max_attempts=10  # Default: 5
```

### Aumentar intervalo entre tentativas
```bash
sleep 10  # Default: 8 segundos
```

### Aumentar timeout de curl
```bash
curl -sf --connect-timeout 10 --max-time 15  # Default: 5s/10s
```

## Benefícios

1. ✅ **Confiabilidade**: Múltiplas tentativas reduzem falsos negativos
2. ✅ **Feedback**: Visualização clara do progresso
3. ✅ **Robustez**: Timeouts apropriados evitam travamentos
4. ✅ **Debugging**: Mensagens claras facilitam troubleshooting
5. ✅ **Escalabilidade**: Funciona com diferentes tempos de inicialização

## Performance

- **Antes**: 30-40 segundos de sleep cego + possível falha
- **Depois**: 
  - Sucesso rápido: ~5-15 segundos
  - Sucesso lento: ~25-40 segundos
  - Falha clara: Após ~40 segundos com recomendações

## Próximos Passos

Para produção, considere:

1. **Endpoint de health check custom**
   - Verificar conexão com banco de dados
   - Validar migrations executadas
   - Verificar dependências externas

2. **Alertas**
   - Notificar em caso de health check falhar
   - Integrar com sistema de monitoramento

3. **Load Balancing**
   - Usar health check para entrada de novo container
   - Implementar graceful shutdown

## Referências

- [FastAPI Health Checks](https://fastapi.tiangolo.com/)
- [Docker Compose Health Checks](https://docs.docker.com/compose/compose-file/#healthcheck)
- [Bash Script Best Practices](https://mywiki.wooledge.org/BashGuide)
