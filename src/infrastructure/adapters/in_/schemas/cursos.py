"""Contratos HTTP (Request/Response) del concern de cursos."""

from pydantic import BaseModel, ConfigDict, Field

from src.domain.entities.curso import EstadoCurso


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
        examples=["Algoritmos y Estructuras de Datos"],
    )
    codigo: str = Field(
        max_length=64,
        description="Código único del curso",
        examples=["CS-2025-001"],
    )
    descripcion: str = Field(
        default="",
        max_length=2000,
        description="Descripción detallada del curso",
        examples=["Curso fundamental sobre algoritmos y estructuras de datos."],
    )
    moodle_course_id: str = Field(
        default="",
        max_length=64,
        description="ID del curso en Moodle (opcional)",
        examples=["5"],
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
    """Respuesta completa de un curso individual."""

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

    id: str = Field(
        description="UUID único del curso",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    nombre: str = Field(
        description="Nombre del curso", examples=["Algoritmos y Estructuras de Datos"]
    )
    codigo: str = Field(description="Código del curso", examples=["CS-2025-001"])
    descripcion: str = Field(description="Descripción del curso", default="")
    moodle_course_id: str = Field(description="ID del curso en Moodle", default="")
    estado: str = Field(
        description="Estado del curso (activo, inactivo)", examples=["activo"]
    )
    docente_id: str | None = Field(
        description="UUID del docente responsable", default=None
    )


class UpdateCourseRequest(BaseModel):
    """Campos editables de un curso (los que el sync de Moodle no sobreescribe)."""

    model_config = ConfigDict(extra="forbid")

    descripcion: str | None = Field(
        default=None, max_length=1000, description="Descripción del curso"
    )
    estado: EstadoCurso | None = Field(
        default=None, description="Estado del curso (activo | inactivo)"
    )


class CursoSyncItem(BaseModel):
    """Curso proveniente de Moodle (vía ms-integracion-lms)."""

    model_config = ConfigDict(extra="forbid")

    moodle_course_id: str = Field(..., description="ID del curso en Moodle")
    nombre: str = Field(..., max_length=255, description="Nombre del curso")
    codigo: str = Field(default="", max_length=50, description="Código (opcional)")


class CursosSyncRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cursos: list[CursoSyncItem]


class CursosSyncResponse(BaseModel):
    procesados: int = Field(..., description="Cursos recibidos")
    creados: int = Field(..., description="Cursos nuevos insertados")
    actualizados: int = Field(..., description="Cursos existentes actualizados")
