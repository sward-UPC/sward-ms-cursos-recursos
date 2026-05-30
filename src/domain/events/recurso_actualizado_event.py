from dataclasses import dataclass, field
from uuid import UUID, uuid4
from sward_shared.events.domain_event import DomainEvent


@dataclass
class RecursoActualizadoEvent(DomainEvent):
    recurso_id: UUID = field(default_factory=uuid4)
    curso_id: UUID = field(default_factory=uuid4)
    source: str = "sward-ms-cursos-recursos"

    @property
    def event_type(self) -> str:
        return "sward.cursos.RecursoActualizado"
