"""
API Aponta - Backend para Extensão Azure DevOps

Aplicação FastAPI com documentação Swagger automática.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import get_settings
from app.routers import atividades, integracao, projetos

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: as migrações são executadas pelo scripts/start.sh
    yield


__version__ = "0.1.0"

# Criar aplicação FastAPI
app = FastAPI(
    title="API Aponta",
    description="""
    Backend para extensão Azure DevOps.

    ## Funcionalidades

    * **Atividades** - CRUD completo para gerenciamento de atividades
    """,
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Logging de inicialização
print(f"🚀 API Aponta inicializada - Schema: {settings.database_schema}")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar origens permitidas
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers
app.include_router(atividades.router, prefix="/api/v1")

app.include_router(integracao.router, prefix="/api/v1")

app.include_router(projetos.router)


@app.get(
    "/",
    tags=["Health"],
    summary="Health Check",
    description="Verifica se a API está funcionando.",
)
@app.get("/healthz", tags=["Health"], include_in_schema=False)
def health_check():
    """Endpoint de health check."""
    return {
        "status": "healthy",
        "version": __version__,
        "environment": settings.environment,
    }


@app.get(
    "/api/v1", tags=["Health"], summary="API Info", description="Informações da API."
)
def api_info():
    """Endpoint com informações da API."""
    return {
        "name": "API Aponta",
        "version": __version__,
        "docs": "/docs",
        "redoc": "/redoc",
    }
