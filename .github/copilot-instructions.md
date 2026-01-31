🤖 Copilot Instructions - Backend Aponta
Este documento define as regras de arquitetura, padrões de código e restrições de infraestrutura para o projeto Aponta Backend (FastAPI/Python 3.12).

🏗️ Contexto da Arquitetura
Ambiente Profissional (2026): O deploy é 100% automatizado via GitHub Actions e GitHub Container Registry (GHCR).
Hospedagem: VPS Ubuntu em /home/ubuntu/aponta-sefaz/.
Diretório de Staging: /home/ubuntu/aponta-sefaz/staging/backend/.
Infraestrutura Compartilhada: O Proxy (Nginx) e o Banco de Dados (Postgres 15) vivem no diretório /shared/.

🛡️ Regras de Ouro (Imutáveis)
1. Conexão com Banco de Dados e Alembic
Escapamento de Strings: Ao configurar a URL do SQLAlchemy no alembic/env.py, deve-se obrigatoriamente usar .replace('%', '%%').
Motivo: Evitar o erro ValueError: invalid interpolation syntax causado pelo configparser do Python ao interpretar caracteres especiais na string de conexão.
Schemas: O sistema utiliza schemas isolados por ambiente; em Staging, o schema é obrigatoriamente aponta_sefaz_staging.

2. Redes e Comunicação Interna
Docker Network: O serviço deve pertencer à rede externa aponta-shared-network.
Network Alias: O container de backend deve possuir o alias de rede api para que o frontend consiga localizá-lo via DNS interno do Docker.
Portas: Nenhuma porta deve ser exposta diretamente para o host (host port mapping) no arquivo docker-compose.yml de Staging ou Produção; a comunicação é feita exclusivamente via rede interna.

3. CI/CD e Deployment
Imutabilidade: Não sugerir builds locais na VPS ou uso de rsync para sincronizar código-fonte.
Workflow: O deploy consiste em: Build da Imagem (GitHub) -> Push (GHCR) -> SSH (VPS) -> docker compose pull.

🚫 Restrições Críticas (Nunca Fazer)
Arquivos Proibidos: Nunca sugerir a criação ou manipulação de arquivos chamados nul, pois são nomes reservados do Windows e causam falhas fatais no Git.
CORS: As configurações de CORS devem permitir as origens https://staging-aponta.treit.com.br e https://aponta.treit.com.br.
Configuração Local: Ignorar sugestões de arquivos .env manuais para rodar as migrações na VPS; as migrações devem ser executadas pelo container em tempo de inicialização.

🛠️ Stack Tecnológica de Referência
Linguagem: Python 3.12.
Framework: FastAPI.
ORM: SQLAlchemy + Alembic.
Banco de Dados: PostgreSQL 15 (Alpine).
Servidor: Uvicorn.