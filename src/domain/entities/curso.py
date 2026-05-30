from dataclasses import dataclass, field
from enum import StrEnum
from uuid import UUID, uuid4


class EstadoCurso(StrEnum):
    ACTIVO = "activo"
    INACTIVO = "inactivo"


@dataclass
class Curso:
    id: UUID = field(default_factory=uuid4)
    nombre: str = ""
    codigo: str = ""
    descripcion: str = ""
    moodle_course_id: str = ""
    estado: EstadoCurso = EstadoCurso.ACTIVO
    docente_id: UUID | None = None
