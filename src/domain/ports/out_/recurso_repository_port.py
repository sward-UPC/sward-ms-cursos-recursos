from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID
from src.domain.entities.metadata_recurso import MetadataRecurso
from src.domain.entities.recurso_educativo import RecursoEducativo
from src.domain.value_objects.tipo_recurso import NivelDificultad, TipoRecurso


@dataclass
class CriteriosBusqueda:
    curso_id: UUID | None = None
    tipo: TipoRecurso | None = None
    nivel_dificultad: NivelDificultad | None = None
    concepto_id: str | None = None
    limit: int = 10


class RecursoRepositoryPort(ABC):
    @abstractmethod
    async def save(
        self, recurso: RecursoEducativo, metadata: MetadataRecurso | None = None
    ) -> RecursoEducativo: ...
    @abstractmethod
    async def find_by_id(self, id: UUID) -> RecursoEducativo | None: ...
    @abstractmethod
    async def find_candidatos(
        self, criterios: CriteriosBusqueda
    ) -> list[RecursoEducativo]: ...
    @abstractmethod
    async def find_all(
        self, curso_id: UUID | None = None
    ) -> list[RecursoEducativo]: ...
    @abstractmethod
    async def upsert_by_moodle_id(
        self, recurso: RecursoEducativo
    ) -> tuple[RecursoEducativo, bool]: ...
