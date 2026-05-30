from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class Actividad:
    id: UUID = field(default_factory=uuid4)
    curso_id: UUID = field(default_factory=uuid4)
    titulo: str = ""
    tipo: str = ""
    puntaje_maximo: float = 100.0
    moodle_activity_id: str = ""
