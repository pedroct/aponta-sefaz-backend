# Dockerfile para API Aponta - Producao VPS Hostinger
# Multi-stage build para imagem otimizada

# === Stage 1: Builder ===
FROM python:3.12-slim as builder

WORKDIR /app

# Instala dependencias de build
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# === Stage 2: Production ===
FROM python:3.12-slim

# Cria usuario nao-root para seguranca
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

WORKDIR /app

# Instala apenas runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copia dependencias do builder
COPY --from=builder /root/.local /home/appuser/.local
ENV PATH=/home/appuser/.local/bin:$PATH

# Copia codigo da aplicacao
COPY --chown=appuser:appgroup app ./app
COPY --chown=appuser:appgroup alembic.ini ./alembic.ini
COPY --chown=appuser:appgroup alembic ./alembic
COPY --chown=appuser:appgroup scripts ./scripts

# Permissoes para scripts
RUN chmod +x /app/scripts/start.sh

# Variaveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ENVIRONMENT=production

# Troca para usuario nao-root
USER appuser

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando de inicializacao
CMD ["/app/scripts/start.sh"]
