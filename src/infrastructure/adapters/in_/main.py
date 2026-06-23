import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from scalar_fastapi import get_scalar_api_reference

from src.application.use_cases.gestionar_curso import CursoNoEncontradoError
from src.infrastructure.adapters.in_.cursos_router import router as cursos_router
from src.infrastructure.adapters.in_.cursos_router import (
    service_router as cursos_service_router,
)
from src.infrastructure.adapters.in_.recursos_router import (
    internal_router as recursos_internal_router,
)
from src.infrastructure.adapters.in_.recursos_router import router as recursos_router
from src.infrastructure.adapters.in_.recursos_router import (
    service_router as recursos_service_router,
)
from src.infrastructure.config.settings import settings
from src.infrastructure.db.database import engine

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # El esquema lo gestiona Alembic (`alembic upgrade head` en el entrypoint del
    # contenedor); aquí solo liberamos el engine al apagar.
    yield
    await engine.dispose()


app = FastAPI(
    title="SWARD — Microservicio de Cursos y Recursos",
    version="0.1.0",
    openapi_url="/courses/openapi.json",
    description=(
        "Gestiona el catálogo de cursos y sus recursos educativos asociados, "
        "exponiendo APIs de consulta y administración para la plataforma SWARD."
    ),
    lifespan=lifespan,
    openapi_tags=[
        {"name": "Cursos", "description": "Creación, consulta y gestión de cursos."},
        {
            "name": "Recursos",
            "description": "Gestión de los recursos educativos asociados a los cursos.",
        },
        {"name": "Health", "description": "Sonda de estado del servicio."},
    ],
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    if not settings.is_development:
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )
    return response


@app.exception_handler(CursoNoEncontradoError)
async def curso_no_encontrado_handler(request: Request, exc: CursoNoEncontradoError):
    """Traduce el error de dominio ``CursoNoEncontradoError`` a un 404 HTTP."""
    return JSONResponse(
        status_code=404,
        content={"detail": "Curso no encontrado"},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Error no controlado en %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno del servidor."},
    )


app.include_router(cursos_router)
app.include_router(cursos_service_router)
app.include_router(recursos_router)
app.include_router(recursos_service_router)
app.include_router(recursos_internal_router)


@app.get("/scalar", include_in_schema=False)
async def scalar_docs():
    """Renderiza la referencia de API interactiva (Scalar) del servicio."""
    return get_scalar_api_reference(openapi_url=app.openapi_url, title=app.title)


@app.get("/health", tags=["Health"], summary="Estado del servicio")
async def health():
    """Devuelve el estado de salud del microservicio para sondas de liveness/readiness."""
    return {"status": "ok", "service": settings.service_name}
