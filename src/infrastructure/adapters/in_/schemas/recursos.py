"""Contratos HTTP (Request/Response) del concern de recursos."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.domain.value_objects.tipo_recurso import NivelDificultad, TipoRecurso


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
        examples=["Tutorial: Quicksort"],
    )
    tipo: TipoRecurso = Field(
        description="Tipo de recurso (video, artículo, etc.)", examples=["video"]
    )
    nivel_dificultad: NivelDificultad = Field(
        default=NivelDificultad.INTERMEDIO,
        description="Nivel de dificultad (básico, intermedio, avanzado)",
        examples=["intermedio"],
    )
    url: str = Field(
        default="",
        max_length=2048,
        description="URL del recurso (opcional)",
        examples=["https://example.com/tutorial-quicksort"],
    )
    etiquetas: list[str] = Field(
        default_factory=list,
        max_length=50,
        description="Etiquetas para categorización",
        examples=[["algoritmo", "ordenamiento"]],
    )
    competencia: str = Field(
        default="",
        max_length=255,
        description="Competencia que desarrolla el recurso",
        examples=["Implementar algoritmos de ordenamiento"],
    )
    tiempo_estimado_min: int = Field(
        default=0,
        ge=0,
        le=100000,
        description="Tiempo estimado de estudio en minutos",
        examples=[30],
    )
    concepto_ids: list[str] = Field(
        default_factory=list,
        max_length=200,
        description="IDs de conceptos asociados",
        examples=[["sorting", "divide-and-conquer"]],
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
        examples=["550e8400-e29b-41d4-a716-446655440001"],
    )
    titulo: str = Field(
        description="Título del recurso",
        max_length=255,
        examples=["Tutorial: Quicksort"],
    )
    tipo: str = Field(description="Tipo de recurso", examples=["video"])
    nivel_dificultad: str = Field(
        description="Nivel de dificultad", examples=["intermedio"]
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
        examples=["550e8400-e29b-41d4-a716-446655440001"],
    )
    titulo: str = Field(
        description="Título del recurso", examples=["Tutorial: Quicksort"]
    )
    tipo: str = Field(description="Tipo de recurso", examples=["video"])
    nivel_dificultad: str = Field(
        description="Nivel de dificultad", examples=["intermedio"]
    )
    url: str = Field(
        description="URL del recurso",
        examples=["https://example.com/tutorial-quicksort"],
    )
    seccion: str = Field(
        default="",
        description="Concepto/sección a la que pertenece el recurso",
        examples=["ordenamiento"],
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
        examples=["550e8400-e29b-41d4-a716-446655440001"],
    )
    titulo: str = Field(
        description="Título del recurso", examples=["Tutorial: Quicksort"]
    )
    tipo: str = Field(description="Tipo de recurso", examples=["video"])


class RecursoSyncItem(BaseModel):
    """Actividad de Moodle a propagar como recurso (vía ms-integracion-lms)."""

    model_config = ConfigDict(extra="forbid")

    moodle_activity_id: str = Field(..., description="ID de la actividad en Moodle")
    moodle_course_id: str = Field(
        ..., description="ID del curso en Moodle al que pertenece"
    )
    titulo: str = Field(..., max_length=255, description="Título de la actividad")
    tipo: str = Field(
        default="", description="Tipo de módulo de Moodle (quiz, assign…)"
    )
    url: str = Field(default="", description="Enlace a la actividad en Moodle")
    seccion: str = Field(
        default="", description="Concepto/sección de Moodle a la que pertenece"
    )


class RecursosSyncRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    recursos: list[RecursoSyncItem]


class RecursosSyncResponse(BaseModel):
    procesados: int = Field(..., description="Recursos recibidos")
    creados: int = Field(..., description="Recursos nuevos insertados")
    actualizados: int = Field(..., description="Recursos existentes actualizados")
    omitidos: int = Field(..., description="Recursos omitidos por curso inexistente")
