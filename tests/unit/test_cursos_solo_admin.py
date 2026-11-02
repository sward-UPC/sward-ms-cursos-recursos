"""Crear y editar cursos es cosa del administrador.

POST /courses y PUT /courses/{id} se conformaban con cualquier sesión válida:
un estudiante o un docente recibía 200 y podía crear cursos, cambiar la
descripción de uno o dejarlo inactivo. Solo la asignación del docente exigía
rol de administrador.

Nadie más que el panel del administrador usa esas dos rutas. ms-integracion-lms
mantiene el catálogo por /internal/courses/sync con su X-Service-Key, que no
depende de este cambio.

Las pruebas firman un JWT de verdad con el secreto del servicio, así que pasan
por la misma validación que una petición real; solo el repositorio es falso.
"""

from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from jose import jwt

from src.application.use_cases.gestionar_curso import GestionarCursoUseCase
from src.domain.entities.curso import Curso, EstadoCurso
from src.infrastructure.adapters.in_.main import app
from src.infrastructure.config.settings import settings
from src.infrastructure.dependencies import get_gestionar_curso_uc

COURSES = "/courses"
SIN_PERMISO = ["estudiante", "docente"]


class _RepoEnMemoria:
    def __init__(self):
        self.cursos: dict[UUID, Curso] = {}

    async def find_by_id(self, id: UUID) -> Curso | None:
        return self.cursos.get(id)

    async def find_all(self) -> list[Curso]:
        return list(self.cursos.values())

    async def save(self, curso: Curso) -> Curso:
        self.cursos[curso.id] = curso
        return curso


def _token(rol: str) -> dict:
    ahora = datetime.now(timezone.utc)
    payload = {
        "sub": str(uuid4()),
        "rol": rol,
        "permisos": [],
        "jti": str(uuid4()),
        "type": "access",
        "iat": ahora,
        "exp": ahora + timedelta(minutes=5),
    }
    firmado = jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)
    return {"Authorization": f"Bearer {firmado}"}


@pytest.fixture
def repo():
    repo = _RepoEnMemoria()
    curso = Curso(
        nombre="Estadística",
        codigo="SWARD-EST",
        descripcion="Descripción original",
        moodle_course_id="7",
    )
    repo.cursos[curso.id] = curso
    return repo


@pytest_asyncio.fixture
async def client(repo):
    app.dependency_overrides[get_gestionar_curso_uc] = lambda: GestionarCursoUseCase(
        repo
    )
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


def _el_curso(repo) -> Curso:
    (curso,) = repo.cursos.values()
    return curso


@pytest.mark.parametrize("rol", SIN_PERMISO)
async def test_editar_sin_ser_admin_da_403_y_el_curso_no_cambia(client, repo, rol):
    curso = _el_curso(repo)

    resp = await client.put(
        f"{COURSES}/{curso.id}",
        json={"descripcion": "Cambiada", "estado": "inactivo"},
        headers=_token(rol),
    )

    assert resp.status_code == 403
    assert curso.descripcion == "Descripción original"
    assert curso.estado == EstadoCurso.ACTIVO


@pytest.mark.parametrize("rol", SIN_PERMISO)
async def test_crear_sin_ser_admin_da_403_y_no_se_crea(client, repo, rol):
    resp = await client.post(
        COURSES,
        json={"nombre": "Curso intruso", "codigo": "X-1"},
        headers=_token(rol),
    )

    assert resp.status_code == 403
    assert len(repo.cursos) == 1


async def test_el_admin_edita(client, repo):
    curso = _el_curso(repo)

    resp = await client.put(
        f"{COURSES}/{curso.id}",
        json={"descripcion": "Nueva descripción", "estado": "inactivo"},
        headers=_token("administrador"),
    )

    assert resp.status_code == 200
    assert resp.json()["descripcion"] == "Nueva descripción"
    assert resp.json()["estado"] == "inactivo"
    assert curso.estado == EstadoCurso.INACTIVO


async def test_el_admin_crea(client, repo):
    resp = await client.post(
        COURSES,
        json={"nombre": "Cálculo I", "codigo": "MA101"},
        headers=_token("administrador"),
    )

    assert resp.status_code == 201
    assert resp.json()["codigo"] == "MA101"
    assert len(repo.cursos) == 2


@pytest.mark.parametrize("rol", SIN_PERMISO)
async def test_leer_sigue_abierto_a_cualquier_sesion(client, repo, rol):
    # El panel del estudiante y el del docente listan el catálogo con su JWT.
    curso = _el_curso(repo)

    lista = await client.get(COURSES, headers=_token(rol))
    detalle = await client.get(f"{COURSES}/{curso.id}", headers=_token(rol))

    assert lista.status_code == 200
    assert detalle.status_code == 200
