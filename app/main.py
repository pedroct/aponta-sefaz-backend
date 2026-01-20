"""
API Aponta - Backend para Extensão Azure DevOps

Aplicação FastAPI com documentação Swagger automática.
"""

import logging
import traceback
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from app.config import get_settings
from app.routers import atividades, apontamentos, integracao, projetos, user, work_items, timesheet
from app.services.seed import ensure_seed_data

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: as migrações são executadas pelo scripts/start.sh
    ensure_seed_data()
    yield


__version__ = "0.1.0"

# Criar aplicação FastAPI
app = FastAPI(
    title="API Aponta",
    description="""
    Backend para extensão Azure DevOps.

    ## Funcionalidades

    * **Atividades** - CRUD completo para gerenciamento de atividades
    * **Apontamentos** - Registro de horas trabalhadas em work items do Azure DevOps
    """,
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Logging de inicialização
logger.info(f"API Aponta inicializada - Schema: {settings.database_schema}")

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions."""
    logger.error(f"Unhandled exception: {exc}")
    logger.error(f"Request: {request.method} {request.url}")
    logger.error(f"Traceback: {traceback.format_exc()}")

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "error": str(exc),
            "type": type(exc).__name__
        },
    )

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers
app.include_router(atividades.router, prefix="/api/v1")

app.include_router(apontamentos.router, prefix="/api/v1")

app.include_router(integracao.router, prefix="/api/v1")

app.include_router(projetos.router)

app.include_router(user.router, prefix="/api/v1")

app.include_router(work_items.router, prefix="/api/v1")

app.include_router(timesheet.router, prefix="/api/v1")


@app.get(
    "/",
    tags=["Health"],
    summary="Health Check",
    description="Verifica se a API está funcionando.",
)
@app.get("/health", tags=["Health"], include_in_schema=False)
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
