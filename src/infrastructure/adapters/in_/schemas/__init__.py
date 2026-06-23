"""Contratos Pydantic (Request/Response) del adaptador de entrada HTTP.

Organizados por concern (cursos, recursos) en vez de un único archivo, según
buenas prácticas de organización. Se re-exportan aquí para que las rutas
importen desde `...adapters.in_.schemas` sin conocer el submódulo.
"""

from .cursos import (
    CreateCourseRequest,
    CursoDetailResponse,
    CursoResponse,
    CursosSyncRequest,
    CursosSyncResponse,
    CursoSyncItem,
    UpdateCourseRequest,
)
from .recursos import (
    CreateResourceRequest,
    CreateResourceResponse,
    RecursoDetailResponse,
    RecursoResponse,
    RecursosSyncRequest,
    RecursosSyncResponse,
    RecursoSyncItem,
)

__all__ = [
    "CreateCourseRequest",
    "CursoResponse",
    "CursoDetailResponse",
    "UpdateCourseRequest",
    "CursoSyncItem",
    "CursosSyncRequest",
    "CursosSyncResponse",
    "CreateResourceRequest",
    "RecursoResponse",
    "RecursoDetailResponse",
    "CreateResourceResponse",
    "RecursoSyncItem",
    "RecursosSyncRequest",
    "RecursosSyncResponse",
]
