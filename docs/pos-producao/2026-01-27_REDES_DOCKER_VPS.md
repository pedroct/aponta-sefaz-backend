# Análise de Redes Docker - VPS Aponta

**Data:** 27 de Janeiro de 2026  
**Autor:** Análise automatizada via GitHub Copilot  
**VPS:** 92.112.178.252

---

## 📋 Resumo

A infraestrutura Docker na VPS utiliza uma **rede compartilhada** (`aponta-shared-network`) para comunicação entre todos os containers do sistema Aponta.

---

## 🌐 Redes Docker Disponíveis

| Rede | ID | Driver | Uso Atual |
|------|----|--------|-----------|
| **aponta-shared-network** | b9088369ac87 | bridge | ✅ Rede principal - todos os containers |
| api-aponta-vps_default | 369e27ae60f9 | bridge | ⚪ Vazia (legado/não utilizada) |
| sefaz-ceara-network | 78ad764ad14c | bridge | ⚪ Vazia (legado/não utilizada) |
| bridge | b92e6af672d8 | bridge | Default do Docker |
| host | 01efdaec9766 | host | Rede do sistema |
| none | 57b8342de416 | null | Sem rede |

---

## 📦 Containers Ativos

### Visão Geral

| Container | Status | Uptime | Portas Expostas |
|-----------|--------|--------|-----------------|
| **nginx-aponta** | 🟢 healthy | 30 horas | 80, 443 → externo |
| **api-aponta-prod** | 🟢 healthy | 27 horas | 8000 → externo |
| **api-aponta-staging** | 🟢 healthy | 28 horas | 8000 (interno) |
| **fe-aponta-prod** | 🟢 healthy | 31 horas | 80 (interno) |
| **fe-aponta-staging** | 🟢 healthy | 31 horas | 80 (interno) |
| **postgres-aponta** | 🟢 healthy | 6 dias | 5432 → externo |

---

## 🔗 Rede Principal: `aponta-shared-network`

### Topologia

```
                    ┌─────────────────────────────────────────────┐
                    │         aponta-shared-network               │
                    │              (172.18.0.0/16)                │
                    └─────────────────────────────────────────────┘
                                        │
        ┌───────────────────────────────┼───────────────────────────────┐
        │                               │                               │
        ▼                               ▼                               ▼
┌───────────────┐              ┌───────────────┐              ┌───────────────┐
│ nginx-aponta  │              │postgres-aponta│              │               │
│ 172.18.0.7    │              │ 172.18.0.3    │              │               │
│ :80, :443     │              │ :5432         │              │               │
└───────┬───────┘              └───────────────┘              │               │
        │                                                      │               │
        ├──────────────────┬───────────────────┐              │               │
        │                  │                   │              │               │
        ▼                  ▼                   ▼              ▼               ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐ ┌───────────────┐
│api-aponta-prod│  │api-aponta-    │  │fe-aponta-prod │ │fe-aponta-     │
│ 172.18.0.4    │  │staging        │  │ 172.18.0.5    │ │staging        │
│ :8000         │  │ 172.18.0.2    │  │ :80           │ │ 172.18.0.6    │
└───────────────┘  │ :8000         │  └───────────────┘ │ :80           │
                   └───────────────┘                    └───────────────┘
```

### Endereços IP

| Container | IP na Rede | Máscara |
|-----------|------------|---------|
| api-aponta-staging | 172.18.0.2 | /16 |
| postgres-aponta | 172.18.0.3 | /16 |
| api-aponta-prod | 172.18.0.4 | /16 |
| fe-aponta-prod | 172.18.0.5 | /16 |
| fe-aponta-staging | 172.18.0.6 | /16 |
| nginx-aponta | 172.18.0.7 | /16 |

---

## 🚪 Portas Expostas para Internet

| Porta | Container | Serviço | Acesso |
|-------|-----------|---------|--------|
| **80** | nginx-aponta | HTTP | Público |
| **443** | nginx-aponta | HTTPS | Público |
| **8000** | api-aponta-prod | API (debug?) | ⚠️ Público |
| **5432** | postgres-aponta | PostgreSQL | ⚠️ Público |

### ⚠️ Alertas de Segurança

1. **Porta 8000 exposta** - API de produção acessível diretamente, bypass do Nginx
2. **Porta 5432 exposta** - PostgreSQL acessível da internet

---

## 🔄 Comunicação Interna

### Como os containers se comunicam

Dentro da rede `aponta-shared-network`, os containers podem se comunicar usando o **nome do container** como hostname:

```bash
# Nginx → API Production
http://api-aponta-prod:8000

# Nginx → API Staging  
http://api-aponta-staging:8000

# Nginx → Frontend Production
http://fe-aponta-prod:80

# Nginx → Frontend Staging
http://fe-aponta-staging:80

# API → PostgreSQL
postgresql://postgres-aponta:5432/database
```

### Fluxo de Requisições

```
Internet                    VPS (92.112.178.252)
    │
    │  :443 HTTPS
    ▼
┌─────────────┐
│   Nginx     │──────┐
│ (proxy)     │      │
└─────────────┘      │
                     │
      ┌──────────────┼──────────────┐
      │              │              │
      ▼              ▼              ▼
┌──────────┐  ┌──────────┐  ┌──────────┐
│ /api/*   │  │ /staging │  │ /* (fe)  │
│          │  │ /api/*   │  │          │
│ api-prod │  │ api-stg  │  │ fe-prod  │
│ :8000    │  │ :8000    │  │ :80      │
└──────────┘  └──────────┘  └──────────┘
      │              │
      └──────┬───────┘
             │
             ▼
      ┌──────────┐
      │ postgres │
      │ :5432    │
      └──────────┘
```

---

## 📊 Redes Não Utilizadas

### api-aponta-vps_default
- **Status:** Vazia
- **Origem provável:** Docker Compose antigo criou automaticamente
- **Ação sugerida:** Pode ser removida

### sefaz-ceara-network
- **Status:** Vazia
- **Origem provável:** Configuração anterior/teste
- **Ação sugerida:** Pode ser removida

### Comando para limpeza (opcional)
```bash
# Verificar se realmente estão vazias
sudo docker network inspect api-aponta-vps_default
sudo docker network inspect sefaz-ceara-network

# Remover se confirmado
sudo docker network rm api-aponta-vps_default
sudo docker network rm sefaz-ceara-network
```

---

## 🛠️ Comandos Úteis

### Verificar redes
```bash
# Listar todas as redes
sudo docker network ls

# Inspecionar rede específica
sudo docker network inspect aponta-shared-network

# Ver containers em uma rede
sudo docker network inspect aponta-shared-network --format '{{range .Containers}}{{.Name}} ({{.IPv4Address}}){{println}}{{end}}'
```

### Verificar conectividade
```bash
# Testar comunicação entre containers
sudo docker exec nginx-aponta ping -c 3 api-aponta-prod
sudo docker exec nginx-aponta ping -c 3 postgres-aponta

# Ver portas abertas
sudo docker port api-aponta-prod
```

### Gerenciar redes
```bash
# Criar nova rede
sudo docker network create --driver bridge minha-rede

# Conectar container a rede
sudo docker network connect aponta-shared-network meu-container

# Desconectar container
sudo docker network disconnect aponta-shared-network meu-container
```

---

## 📝 Configuração no Docker Compose

Para manter os containers na mesma rede, o `docker-compose.yml` deve incluir:

```yaml
version: '3.8'

services:
  api:
    # ...
    networks:
      - aponta-shared-network

  frontend:
    # ...
    networks:
      - aponta-shared-network

  nginx:
    # ...
    networks:
      - aponta-shared-network

networks:
  aponta-shared-network:
    external: true  # Usa rede existente
```

---

## 🔐 Recomendações de Segurança

### Imediato

1. **Remover exposição da porta 8000**
   ```bash
   # Editar docker-compose de produção
   # Remover "0.0.0.0:8000->8000" 
   # Manter apenas comunicação interna via Nginx
   ```

2. **Restringir acesso ao PostgreSQL**
   ```bash
   # Opção 1: Remover bind externo
   # Opção 2: Usar firewall (ufw)
   sudo ufw deny 5432
   sudo ufw allow from 172.18.0.0/16 to any port 5432
   ```

### Médio Prazo

3. **Implementar network policies** (se usar Kubernetes no futuro)
4. **Segmentar redes por ambiente** (staging vs production)

---

## 📚 Documentação Relacionada

- [2026-01-27_ANALISE_ARQUITETURA_DEVOPS.md](./2026-01-27_ANALISE_ARQUITETURA_DEVOPS.md) - Arquitetura geral
- [2026-01-27_SINCRONIZACAO_CODIGO_LOCAL_VPS.md](./2026-01-27_SINCRONIZACAO_CODIGO_LOCAL_VPS.md) - Sincronização de código

---

*Documento gerado a partir da análise da infraestrutura Docker na VPS 92.112.178.252*
