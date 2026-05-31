from uuid import UUID

from fastapi import APIRouter, Body, Depends, Query, status
from pydantic import BaseModel, ConfigDict, Field

from src.application.use_cases.buscar_recursos_candidatos import (
    BuscarRecursosCandidatosUseCase,
)
from src.application.use_cases.gestionar_recurso import (
    GestionarRecursoCommand,
    GestionarRecursoUseCase,
)
from src.domain.ports.out_.recurso_repository_port import CriteriosBusqueda
from src.domain.value_objects.tipo_recurso import NivelDificultad, TipoRecurso
from src.infrastructure.dependencies import (
    get_buscar_candidatos_uc,
    get_gestionar_recurso_uc,
    require_jwt,
    require_service_key,
)

# Endpoints de gestión de recursos: exigen un JWT de acceso válido (usuario final).
router = APIRouter(
    prefix="/resources", tags=["Recursos"], dependencies=[Depends(require_jwt)]
)

# Endpoint servicio-a-servicio (consumido por recomendacion): se valida vía
# X-Service-Key en lugar de JWT. En desarrollo, sin claves configuradas, no bloquea.
service_router = APIRouter(
    prefix="/resources", tags=["Recursos"], dependencies=[Depends(require_service_key)]
)


class CreateResourceRequest(BaseModel):
    """Solicitud para crear un nuevo recurso."""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "curso_id": "550e8400-e29b-41d4-a716-446655440000",
                "titulo": "Tutorial: Quicksort",
                "tipo": "video",
                "nivel_dificultad": "intermedio",
                "url": "https://example.com/tutorial-quicksort",
                "etiquetas": ["algoritmo", "ordenamiento"],
                "competencia": "Implementar algoritmos de ordenamiento",
                "tiempo_estimado_min": 30,
                "concepto_ids": ["sorting", "divide-and-conquer"],
            }
        },
    )

    curso_id: UUID = Field(description="UUID del curso al que pertenece el recurso")
    titulo: str = Field(
        max_length=255,
        description="Título del recurso",
        example="Tutorial: Quicksort",
    )
    tipo: TipoRecurso = Field(
        description="Tipo de recurso (video, artículo, etc.)", example="video"
    )
    nivel_dificultad: NivelDificultad = Field(
        default=NivelDificultad.INTERMEDIO,
        description="Nivel de dificultad (básico, intermedio, avanzado)",
        example="intermedio",
    )
    url: str = Field(
        default="",
        max_length=2048,
        description="URL del recurso (opcional)",
        example="https://example.com/tutorial-quicksort",
    )
    etiquetas: list[str] = Field(
        default_factory=list,
        max_length=50,
        description="Etiquetas para categorización",
        example=["algoritmo", "ordenamiento"],
    )
    competencia: str = Field(
        default="",
        max_length=255,
        description="Competencia que desarrolla el recurso",
        example="Implementar algoritmos de ordenamiento",
    )
    tiempo_estimado_min: int = Field(
        default=0,
        ge=0,
        le=100000,
        description="Tiempo estimado de estudio en minutos",
        example=30,
    )
    concepto_ids: list[str] = Field(
        default_factory=list,
        max_length=200,
        description="IDs de conceptos asociados",
        example=["sorting", "divide-and-conquer"],
    )


class RecursoResponse(BaseModel):
    """Respuesta que contiene información de un recurso."""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440001",
                "titulo": "Tutorial: Quicksort",
                "tipo": "video",
                "nivel_dificultad": "intermedio",
            }
        },
    )

    id: str = Field(
        description="UUID único del recurso",
        example="550e8400-e29b-41d4-a716-446655440001",
    )
    titulo: str = Field(
        description="Título del recurso", max_length=255, example="Tutorial: Quicksort"
    )
    tipo: str = Field(description="Tipo de recurso", example="video")
    nivel_dificultad: str = Field(
        description="Nivel de dificultad", example="intermedio"
    )


class RecursoDetailResponse(BaseModel):
    """Respuesta que contiene información detallada de un recurso."""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440001",
                "titulo": "Tutorial: Quicksort",
                "tipo": "video",
                "nivel_dificultad": "intermedio",
                "url": "https://example.com/tutorial-quicksort",
            }
        },
    )

    id: str = Field(
        description="UUID único del recurso",
        example="550e8400-e29b-41d4-a716-446655440001",
    )
    titulo: str = Field(description="Título del recurso", example="Tutorial: Quicksort")
    tipo: str = Field(description="Tipo de recurso", example="video")
    nivel_dificultad: str = Field(
        description="Nivel de dificultad", example="intermedio"
    )
    url: str = Field(
        description="URL del recurso", example="https://example.com/tutorial-quicksort"
    )


class CreateResourceResponse(BaseModel):
    """Respuesta de creación de recurso."""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440001",
                "titulo": "Tutorial: Quicksort",
                "tipo": "video",
            }
        },
    )

    id: str = Field(
        description="UUID único del recurso creado",
        example="550e8400-e29b-41d4-a716-446655440001",
    )
    titulo: str = Field(description="Título del recurso", example="Tutorial: Quicksort")
    tipo: str = Field(description="Tipo de recurso", example="video")


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=CreateResourceResponse,
    responses={
        201: {
            "description": "Recurso creado exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "id": "550e8400-e29b-41d4-a716-446655440001",
                        "titulo": "Tutorial: Quicksort",
                        "tipo": "video",
                    }
                }
            },
        },
        400: {"description": "Solicitud inválida. Parámetros incorrectos."},
        401: {"description": "No autorizado. JWT inválido o expirado."},
        404: {"description": "Curso no encontrado."},
        422: {"description": "Entidad no procesable. Validación de datos fallida."},
        500: {"description": "Error interno del servidor."},
    },
)
async def create_resource(
    body: CreateResourceRequest = Body(..., description="Datos del recurso a crear"),
    uc: GestionarRecursoUseCase = Depends(get_gestionar_recurso_uc),
):
    """Crea un nuevo recurso educativo en el sistema.

    **Flujo:** 1. Valida JWT 2. Valida existencia del curso 3. Crea recurso en base de datos 4. Retorna confirmación

    **SLA:** <100ms | **Auth:** JWT | **Rate Limit:** 60 req/min
    """
    r = await uc.crear(GestionarRecursoCommand(**body.model_dump()))
    return {"id": str(r.id), "titulo": r.titulo, "tipo": r.tipo}


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=list[RecursoResponse],
    responses={
        200: {
            "description": "Lista de recursos obtenida exitosamente",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "550e8400-e29b-41d4-a716-446655440001",
                            "titulo": "Tutorial: Quicksort",
                            "tipo": "video",
                            "nivel_dificultad": "intermedio",
                        }
                    ]
                }
            },
        },
        401: {"description": "No autorizado. JWT inválido o expirado."},
        500: {"description": "Error interno del servidor."},
    },
)
async def list_resources(
    curso_id: UUID | None = Query(
        default=None,
        description="UUID del curso para filtrar recursos (opcional)",
    ),
    uc: GestionarRecursoUseCase = Depends(get_gestionar_recurso_uc),
):
    """Obtiene la lista de recursos, opcionalmente filtrados por curso.

    **Flujo:** 1. Valida JWT 2. Filtra por curso si se proporciona 3. Retorna lista de recursos

    **SLA:** <100ms | **Auth:** JWT | **Rate Limit:** 120 req/min
    """
    recursos = await uc.listar(curso_id)
    return [
        {
            "id": str(r.id),
            "titulo": r.titulo,
            "tipo": r.tipo,
            "nivel_dificultad": r.nivel_dificultad,
        }
        for r in recursos
    ]


@service_router.get(
    "/candidates",
    status_code=status.HTTP_200_OK,
    response_model=list[RecursoDetailResponse],
    responses={
        200: {
            "description": "Lista de recursos candidatos obtenida exitosamente",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "550e8400-e29b-41d4-a716-446655440001",
                            "titulo": "Tutorial: Quicksort",
                            "tipo": "video",
                            "nivel_dificultad": "intermedio",
                            "url": "https://example.com/tutorial-quicksort",
                        }
                    ]
                }
            },
        },
        400: {"description": "Solicitud inválida. Parámetros incorrectos."},
        401: {"description": "No autorizado. Service Key inválida."},
        422: {"description": "Entidad no procesable. Validación de datos fallida."},
        500: {"description": "Error interno del servidor."},
    },
)
async def get_candidates(
    courseId: UUID | None = Query(
        default=None,
        description="UUID del curso para filtrar candidatos (opcional)",
    ),
    tipo: TipoRecurso | None = Query(
        default=None,
        description="Tipo de recurso para filtrar candidatos (opcional)",
    ),
    nivel: NivelDificultad | None = Query(
        default=None,
        description="Nivel de dificultad para filtrar candidatos (opcional)",
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Cantidad máxima de candidatos a retornar",
    ),
    uc: BuscarRecursosCandidatosUseCase = Depends(get_buscar_candidatos_uc),
):
    """Obtiene recursos candidatos para recomendación (endpoint servicio-a-servicio).

    **Flujo:** 1. Valida Service Key 2. Aplica criterios de búsqueda 3. Retorna lista paginada

    **SLA:** <200ms | **Auth:** Service Key | **Rate Limit:** 300 req/min
    """
    recursos = await uc.execute(
        CriteriosBusqueda(
            curso_id=courseId, tipo=tipo, nivel_dificultad=nivel, limit=limit
        )
    )
    return [
        {
            "id": str(r.id),
            "titulo": r.titulo,
            "tipo": r.tipo,
            "nivel_dificultad": r.nivel_dificultad,
            "url": r.url,
        }
        for r in recursos
    ]
