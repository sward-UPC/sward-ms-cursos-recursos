"""El docente a cargo del curso: quién lo ve y quién puede ponerlo.

De este dato dependen dos cosas visibles: el panel del docente lista solo sus
cursos, y las alertas de estudiante en riesgo van a quien dicta el curso. Por eso
asignarlo exige rol de administrador, mientras que el resto de /courses se
conforma con una sesión válida.
"""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from fastapi import HTTPException

from src.application.use_cases.gestionar_curso import (
    CursoNoEncontradoError,
    GestionarCursoCommand,
    GestionarCursoUseCase,
)
from src.infrastructure.dependencies import require_admin


@pytest.fixture
def use_case():
    repo = AsyncMock()
    repo.save.side_effect = lambda c: c
    return repo, GestionarCursoUseCase(repo)


@pytest.mark.asyncio
async def test_asigna_el_docente(use_case):
    repo, uc = use_case
    curso = await GestionarCursoUseCase(repo).crear(
        GestionarCursoCommand(nombre="Estadística", codigo="SWARD-EST")
    )
    repo.find_by_id.return_value = curso
    docente = uuid4()

    actualizado = await uc.asignar_docente(curso.id, docente)

    assert actualizado.docente_id == docente


@pytest.mark.asyncio
async def test_none_lo_deja_sin_docente(use_case):
    repo, uc = use_case
    curso = await GestionarCursoUseCase(repo).crear(
        GestionarCursoCommand(nombre="Estadística", codigo="SWARD-EST", docente_id=uuid4())
    )
    repo.find_by_id.return_value = curso

    actualizado = await uc.asignar_docente(curso.id, None)

    assert actualizado.docente_id is None


@pytest.mark.asyncio
async def test_curso_inexistente(use_case):
    repo, uc = use_case
    repo.find_by_id.return_value = None

    with pytest.raises(CursoNoEncontradoError):
        await uc.asignar_docente(uuid4(), uuid4())


def test_el_administrador_pasa():
    usuario = {"sub": str(uuid4()), "rol": "administrador"}
    assert require_admin(usuario) is usuario


@pytest.mark.parametrize("rol", ["docente", "estudiante", None])
def test_los_demas_no(rol):
    with pytest.raises(HTTPException) as e:
        require_admin({"sub": str(uuid4()), "rol": rol})
    assert e.value.status_code == 403
