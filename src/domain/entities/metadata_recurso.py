from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class MetadataRecurso:
    id: UUID = field(default_factory=uuid4)
    recurso_id: UUID = field(default_factory=uuid4)
    etiquetas: list[str] = field(default_factory=list)
    competencia: str = ""
    tiempo_estimado_min: int = 0
    concepto_ids: list[str] = field(default_factory=list)
