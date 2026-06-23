from dataclasses import dataclass, field
from uuid import UUID
from src.domain.entities.metadata_recurso import MetadataRecurso
from src.domain.entities.recurso_educativo import RecursoEducativo
from src.domain.events.recurso_actualizado_event import RecursoActualizadoEvent
from src.domain.ports.out_.curso_repository_port import CursoRepositoryPort
from src.domain.ports.out_.event_publisher_port import EventPublisherPort
from src.domain.ports.out_.recurso_repository_port import RecursoRepositoryPort
from src.domain.ports.out_.storage_port import StoragePort
from src.domain.value_objects.tipo_recurso import NivelDificultad, TipoRecurso

# Mapeo de tipos de módulo de Moodle al catálogo de tipos de recurso de SWARD.
# Los tipos no contemplados caen en EJERCICIO (default razonable para actividad).
_MOODLE_TIPO_A_RECURSO: dict[str, TipoRecurso] = {
    "quiz": TipoRecurso.QUIZ,
    "assign": TipoRecurso.EJERCICIO,
    "workshop": TipoRecurso.EJERCICIO,
    "resource": TipoRecurso.LECTURA,
    "page": TipoRecurso.LECTURA,
    "book": TipoRecurso.LECTURA,
    "url": TipoRecurso.LECTURA,
    "label": TipoRecurso.LECTURA,
    "lesson": TipoRecurso.PRESENTACION,
    "scorm": TipoRecurso.PRESENTACION,
    "forum": TipoRecurso.EJERCICIO,
}


def _mapear_tipo_moodle(tipo: str) -> TipoRecurso:
    return _MOODLE_TIPO_A_RECURSO.get((tipo or "").lower(), TipoRecurso.EJERCICIO)


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


@dataclass
class RecursoSyncItemCommand:
    """Actividad de Moodle a propagar como recurso (vía ms-integracion-lms)."""

    moodle_activity_id: str
    moodle_course_id: str
    titulo: str
    tipo: str = ""
    url: str = ""
    seccion: str = ""


@dataclass
class SincronizarRecursosCommand:
    recursos: list[RecursoSyncItemCommand]


@dataclass
class SincronizarRecursosResultado:
    procesados: int
    creados: int
    actualizados: int
    omitidos: int


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


class SincronizarRecursosUseCase:
    """Sincroniza actividades de Moodle como recursos (upsert idempotente).

    Resuelve el ``curso_id`` interno buscando el curso por su
    ``moodle_course_id`` (el sync de cursos corre antes). Si el curso aún no
    existe en el catálogo, omite ese recurso.
    """

    def __init__(
        self,
        recurso_repo: RecursoRepositoryPort,
        curso_repo: CursoRepositoryPort,
    ):
        self._recurso_repo = recurso_repo
        self._curso_repo = curso_repo

    async def execute(
        self, cmd: SincronizarRecursosCommand
    ) -> SincronizarRecursosResultado:
        creados = 0
        actualizados = 0
        omitidos = 0
        # Cache local para no re-consultar el mismo curso en cada actividad.
        cursos_cache: dict[str, UUID | None] = {}
        for item in cmd.recursos:
            if not item.moodle_activity_id:
                continue
            if item.moodle_course_id not in cursos_cache:
                curso = await self._curso_repo.find_by_moodle_course_id(
                    item.moodle_course_id
                )
                cursos_cache[item.moodle_course_id] = curso.id if curso else None
            curso_id = cursos_cache[item.moodle_course_id]
            if curso_id is None:
                omitidos += 1
                continue
            recurso = RecursoEducativo(
                curso_id=curso_id,
                titulo=item.titulo,
                tipo=_mapear_tipo_moodle(item.tipo),
                url=item.url,
                seccion=item.seccion,
                moodle_resource_id=item.moodle_activity_id,
            )
            _, creado = await self._recurso_repo.upsert_by_moodle_id(recurso)
            creados += int(creado)
            actualizados += int(not creado)
        return SincronizarRecursosResultado(
            procesados=len(cmd.recursos),
            creados=creados,
            actualizados=actualizados,
            omitidos=omitidos,
        )
