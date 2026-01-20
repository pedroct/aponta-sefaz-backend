# Contexto do Projeto - API Aponta VPS

## 📋 Informações Gerais

### Origem
Projeto criado a partir do `api-aponta-supa` para deploy em VPS Hostinger com CloudFlare.

### Repositório
- **GitHub:** https://github.com/pedroct/api-aponta-vps.git
- **Branch atual:** develop
- **Versão:** v0.1.0
- **Status:** ✅ Pronto para deploy em produção

### Producao (VPS Hostinger)
- **Host:** srv1264175.hstgr.cloud
- **IP:** 31.97.16.12
- **SSH:** `ssh root@31.97.16.12`
- **Dominio:** api-aponta.pedroct.com.br
- **CDN/Proxy:** CloudFlare (SSL/TLS Full Strict)
- **Caminho:** /opt/api-aponta-vps

### Desenvolvimento Local (Docker)
- **Container API:** api-aponta-local (porta 8000)
- **Container DB:** postgres-aponta (PostgreSQL 15 compartilhado)
- **Rede:** api-aponta_aponta-network
- **Swagger:** http://localhost:8000/docs

---

## 📚 Documentação Completa

Este projeto possui documentação profissional e abrangente:

### Documentação Técnica
- **README.md** - Visão geral, quick start e badges
- **ARCHITECTURE.md** - Arquitetura detalhada com diagramas
- **API_DOCUMENTATION.md** - Referência completa da API
- **CONTRIBUTING.md** - Guia para contribuidores
- **SECURITY.md** - Políticas de segurança

### Documentacao de Deploy
- **DEPLOY_INSTRUCTIONS.md** - Guia completo de deploy
- **CLOUDFLARE_SETUP.md** - Configuracao CloudFlare
- **CLOUDFLARE_FINAL_SETUP.md** - Setup final SSL
- **ENVIRONMENTS.md** - Ambientes de producao e desenvolvimento

**Total:** 10 documentos | ~8,000 linhas | 100% coverage

---

### Caminhos atuais
- `README.md`
- `docs/architecture/ARCHITECTURE.md`
- `docs/api/API_DOCUMENTATION.md`
- `docs/contributing/CONTRIBUTING.md`
- `docs/security/SECURITY.md`
- `docs/deploy/DEPLOY_INSTRUCTIONS.md`
- `docs/deploy/CLOUDFLARE_SETUP.md`
- `docs/deploy/CLOUDFLARE_FINAL_SETUP.md`
- `docs/deploy/ENVIRONMENTS.md`

---

**Para informações detalhadas, consulte README.md**

**Ultima atualizacao:** 2026-01-18 | **Versao:** 2.2
