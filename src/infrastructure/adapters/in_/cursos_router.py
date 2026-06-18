from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Path, status
from pydantic import BaseModel, ConfigDict, Field

from src.application.use_cases.gestionar_curso import (
    GestionarCursoCommand,
    GestionarCursoUseCase,
)
from src.infrastructure.dependencies import get_gestionar_curso_uc, require_jwt

# Todos los endpoints de /courses exigen un JWT de acceso válido.
router = APIRouter(
    prefix="/courses", tags=["Cursos"], dependencies=[Depends(require_jwt)]
)


class CreateCourseRequest(BaseModel):
    """Solicitud para crear un nuevo curso."""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "nombre": "Algoritmos y Estructuras de Datos",
                "codigo": "CS-2025-001",
                "descripcion": "Curso fundamental sobre algoritmos y estructuras de datos.",
                "moodle_course_id": "5",
            }
        },
    )

    nombre: str = Field(
        max_length=255,
        description="Nombre del curso",
        example="Algoritmos y Estructuras de Datos",
    )
    codigo: str = Field(
        max_length=64,
        description="Código único del curso",
        example="CS-2025-001",
    )
    descripcion: str = Field(
        default="",
        max_length=2000,
        description="Descripción detallada del curso",
        example="Curso fundamental sobre algoritmos y estructuras de datos.",
    )
    moodle_course_id: str = Field(
        default="",
        max_length=64,
        description="ID del curso en Moodle (opcional)",
        example="5",
    )


class CursoResponse(BaseModel):
    """Respuesta que contiene información de un curso."""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "nombre": "Algoritmos y Estructuras de Datos",
                "codigo": "CS-2025-001",
                "descripcion": "Curso fundamental sobre algoritmos.",
                "moodle_course_id": "5",
                "estado": "activo",
                "docente_id": None,
            }
        },
    )

    id: str = Field(description="UUID único del curso")
    nombre: str = Field(description="Nombre del curso", max_length=255)
    codigo: str = Field(description="Código del curso", max_length=64)
    descripcion: str = Field(description="Descripción del curso", default="")
    moodle_course_id: str = Field(description="ID del curso en Moodle", default="")
    estado: str = Field(description="Estado del curso (activo, inactivo)")
    docente_id: str | None = Field(
        description="UUID del docente responsable", default=None
    )


class CursoDetailResponse(BaseModel):
    """Respuesta detallada que contiene información completa de un curso."""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "nombre": "Algoritmos y Estructuras de Datos",
                "codigo": "CS-2025-001",
            }
        },
    )

    id: str = Field(
        description="UUID único del curso",
        example="550e8400-e29b-41d4-a716-446655440000",
    )
    nombre: str = Field(
        description="Nombre del curso", example="Algoritmos y Estructuras de Datos"
    )
    codigo: str = Field(description="Código del curso", example="CS-2025-001")


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=CursoDetailResponse,
    responses={
        201: {
            "description": "Curso creado exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "nombre": "Algoritmos y Estructuras de Datos",
                        "codigo": "CS-2025-001",
                    }
                }
            },
        },
        400: {"description": "Solicitud inválida. Parámetros incorrectos."},
        401: {"description": "No autorizado. JWT inválido o expirado."},
        409: {"description": "Conflicto. Código de curso ya existe."},
        422: {"description": "Entidad no procesable. Validación de datos fallida."},
        500: {"description": "Error interno del servidor."},
    },
)
async def create_course(
    body: CreateCourseRequest = Body(..., description="Datos del curso a crear"),
    uc: GestionarCursoUseCase = Depends(get_gestionar_curso_uc),
):
    """Crea un nuevo curso en el sistema.

    **Flujo:** 1. Valida JWT 2. Valida unicidad del código 3. Crea curso en base de datos 4. Retorna confirmación

    **SLA:** <100ms | **Auth:** JWT | **Rate Limit:** 60 req/min
    """
    c = await uc.crear(GestionarCursoCommand(**body.model_dump()))
    return {"id": str(c.id), "nombre": c.nombre, "codigo": c.codigo}


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=list[CursoResponse],
    responses={
        200: {
            "description": "Lista de cursos obtenida exitosamente",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "550e8400-e29b-41d4-a716-446655440000",
                            "nombre": "Algoritmos y Estructuras de Datos",
                            "codigo": "CS-2025-001",
                            "estado": "activo",
                        }
                    ]
                }
            },
        },
        401: {"description": "No autorizado. JWT inválido o expirado."},
        500: {"description": "Error interno del servidor."},
    },
)
async def list_courses(uc: GestionarCursoUseCase = Depends(get_gestionar_curso_uc)):
    """Obtiene la lista de todos los cursos.

    **Flujo:** 1. Valida JWT 2. Consulta base de datos 3. Retorna lista de cursos

    **SLA:** <100ms | **Auth:** JWT | **Rate Limit:** 120 req/min
    """
    cursos = await uc.listar()
    return [
        {
            "id": str(c.id),
            "nombre": c.nombre,
            "codigo": c.codigo,
            "descripcion": c.descripcion,
            "moodle_course_id": c.moodle_course_id,
            "estado": c.estado if isinstance(c.estado, str) else c.estado.value,
            "docente_id": str(c.docente_id) if c.docente_id else None,
        }
        for c in cursos
    ]


@router.get(
    "/{course_id}",
    status_code=status.HTTP_200_OK,
    response_model=CursoDetailResponse,
    responses={
        200: {
            "description": "Curso obtenido exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "nombre": "Algoritmos y Estructuras de Datos",
                        "codigo": "CS-2025-001",
                    }
                }
            },
        },
        401: {"description": "No autorizado. JWT inválido o expirado."},
        404: {"description": "Curso no encontrado."},
        500: {"description": "Error interno del servidor."},
    },
)
async def get_course(
    course_id: UUID = Path(..., description="UUID del curso a obtener"),
    uc: GestionarCursoUseCase = Depends(get_gestionar_curso_uc),
):
    """Obtiene los detalles de un curso específico por ID.

    **Flujo:** 1. Valida JWT 2. Consulta base de datos 3. Retorna detalles del curso

    **SLA:** <50ms | **Auth:** JWT | **Rate Limit:** 120 req/min
    """
    c = await uc.obtener(course_id)
    if not c:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Curso no encontrado"
        )
    return {"id": str(c.id), "nombre": c.nombre, "codigo": c.codigo}
