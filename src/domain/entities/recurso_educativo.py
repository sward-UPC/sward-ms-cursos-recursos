from dataclasses import dataclass, field
from uuid import UUID, uuid4
from src.domain.value_objects.tipo_recurso import NivelDificultad, TipoRecurso


@dataclass
class RecursoEducativo:
    id: UUID = field(default_factory=uuid4)
    curso_id: UUID = field(default_factory=uuid4)
    titulo: str = ""
    tipo: TipoRecurso = TipoRecurso.LECTURA
    nivel_dificultad: NivelDificultad = NivelDificultad.INTERMEDIO
    url: str = ""
    s3_key: str = ""
    activo: bool = True
    moodle_resource_id: str = ""
