from dataclasses import dataclass, field
from uuid import UUID
from src.domain.entities.metadata_recurso import MetadataRecurso
from src.domain.entities.recurso_educativo import RecursoEducativo
from src.domain.events.recurso_actualizado_event import RecursoActualizadoEvent
from src.domain.ports.out_.event_publisher_port import EventPublisherPort
from src.domain.ports.out_.recurso_repository_port import RecursoRepositoryPort
from src.domain.ports.out_.storage_port import StoragePort
from src.domain.value_objects.tipo_recurso import NivelDificultad, TipoRecurso


@dataclass
class GestionarRecursoCommand:
    curso_id: UUID
    titulo: str
    tipo: TipoRecurso
    nivel_dificultad: NivelDificultad = NivelDificultad.INTERMEDIO
    etiquetas: list[str] = field(default_factory=list)
    competencia: str = ""
    tiempo_estimado_min: int = 0
    url: str = ""
    concepto_ids: list[str] = field(default_factory=list)


class GestionarRecursoUseCase:
    def __init__(
        self,
        repo: RecursoRepositoryPort,
        storage: StoragePort,
        event_publisher: EventPublisherPort,
    ):
        self._repo = repo
        self._storage = storage
        self._event_publisher = event_publisher

    async def crear(self, cmd: GestionarRecursoCommand) -> RecursoEducativo:
        recurso = RecursoEducativo(
            curso_id=cmd.curso_id,
            titulo=cmd.titulo,
            tipo=cmd.tipo,
            nivel_dificultad=cmd.nivel_dificultad,
            url=cmd.url,
        )
        metadata = MetadataRecurso(
            recurso_id=recurso.id,
            etiquetas=cmd.etiquetas,
            competencia=cmd.competencia,
            tiempo_estimado_min=cmd.tiempo_estimado_min,
            concepto_ids=cmd.concepto_ids,
        )
        guardado = await self._repo.save(recurso, metadata)
        self._event_publisher.publish(
            RecursoActualizadoEvent(recurso_id=guardado.id, curso_id=guardado.curso_id)
        )
        return guardado

    async def listar(self, curso_id: UUID | None = None) -> list[RecursoEducativo]:
        return await self._repo.find_all(curso_id)
