"""Fixtures de integración para los endpoints de cursos y recursos (in-process).

La app se ejerce con httpx.AsyncClient + ASGITransport (sin servidor).
Los repositorios Postgres se sustituyen por implementaciones en memoria
compartidas vía dependency_overrides; el StoragePort (S3) y el publisher de
eventos se reemplazan por stubs. Se conserva la lógica real de los casos de uso.
"""

from uuid import UUID

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from src.application.use_cases.buscar_recursos_candidatos import (
    BuscarRecursosCandidatosUseCase,
)
from src.application.use_cases.gestionar_curso import GestionarCursoUseCase
from src.application.use_cases.gestionar_recurso import GestionarRecursoUseCase
from src.domain.entities.actividad import Actividad
from src.domain.entities.curso import Curso
from src.domain.entities.metadata_recurso import MetadataRecurso
from src.domain.entities.recurso_educativo import RecursoEducativo
from src.domain.ports.out_.curso_repository_port import CursoRepositoryPort
from src.domain.ports.out_.recurso_repository_port import (
    CriteriosBusqueda,
    RecursoRepositoryPort,
)
from src.infrastructure.adapters.in_.main import app
from src.infrastructure.dependencies import (
    get_buscar_candidatos_uc,
    get_gestionar_curso_uc,
    get_gestionar_recurso_uc,
    require_jwt,
)

FAKE_PAYLOAD = {
    "sub": "00000000-0000-0000-0000-000000000001",
    "rol": "docente",
    "permisos": ["leer", "escribir"],
    "type": "access",
}


class FakeCursoRepo(CursoRepositoryPort):
    def __init__(self):
        self.cursos: dict[UUID, Curso] = {}
        self.actividades: list[Actividad] = []

    async def find_by_id(self, id: UUID) -> Curso | None:
        return self.cursos.get(id)

    async def save(self, curso: Curso) -> Curso:
        self.cursos[curso.id] = curso
        return curso

    async def find_all(self) -> list[Curso]:
        return list(self.cursos.values())

    async def upsert_by_moodle_id(self, curso: Curso) -> tuple[Curso, bool]:
        for existente in self.cursos.values():
            if existente.moodle_course_id == curso.moodle_course_id:
                existente.nombre = curso.nombre
                return existente, False
        self.cursos[curso.id] = curso
        return curso, True

    async def save_actividad(self, actividad: Actividad) -> Actividad:
        self.actividades.append(actividad)
        return actividad

    async def find_actividades(self, curso_id: UUID) -> list[Actividad]:
        return [a for a in self.actividades if a.curso_id == curso_id]


class FakeRecursoRepo(RecursoRepositoryPort):
    def __init__(self):
        self.recursos: dict[UUID, RecursoEducativo] = {}

    async def save(
        self, recurso: RecursoEducativo, metadata: MetadataRecurso | None = None
    ):
        self.recursos[recurso.id] = recurso
        return recurso

    async def find_by_id(self, id: UUID) -> RecursoEducativo | None:
        return self.recursos.get(id)

    async def find_candidatos(self, criterios: CriteriosBusqueda):
        items = [r for r in self.recursos.values() if r.activo]
        if criterios.curso_id:
            items = [r for r in items if r.curso_id == criterios.curso_id]
        if criterios.tipo:
            items = [r for r in items if r.tipo == criterios.tipo]
        if criterios.nivel_dificultad:
            items = [
                r for r in items if r.nivel_dificultad == criterios.nivel_dificultad
            ]
        return items[: criterios.limit]

    async def find_all(self, curso_id: UUID | None = None):
        items = list(self.recursos.values())
        if curso_id:
            items = [r for r in items if r.curso_id == curso_id]
        return items


class _StubStorage:
    async def upload(self, *args, **kwargs):  # noqa: ANN002, ANN003
        return "s3://stub/key"

    async def generar_url_descarga(self, *args, **kwargs):  # noqa: ANN002, ANN003
        return "https://stub/download"

    async def eliminar(self, *args, **kwargs):  # noqa: ANN002, ANN003
        return None


class _StubEventPublisher:
    def publish(self, event) -> None:  # noqa: ARG002
        return None


@pytest_asyncio.fixture
async def client():
    curso_repo = FakeCursoRepo()
    recurso_repo = FakeRecursoRepo()
    storage = _StubStorage()
    events = _StubEventPublisher()

    app.dependency_overrides[get_gestionar_curso_uc] = lambda: GestionarCursoUseCase(
        curso_repo
    )
    app.dependency_overrides[get_gestionar_recurso_uc] = lambda: (
        GestionarRecursoUseCase(recurso_repo, storage, events)
    )
    app.dependency_overrides[get_buscar_candidatos_uc] = lambda: (
        BuscarRecursosCandidatosUseCase(recurso_repo)
    )
    # Sobreescribe la validación JWT por un payload fake (autenticación simulada).
    app.dependency_overrides[require_jwt] = lambda: FAKE_PAYLOAD

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def anon_client():
    """Cliente sin override de auth: los endpoints protegidos exigen token real."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
