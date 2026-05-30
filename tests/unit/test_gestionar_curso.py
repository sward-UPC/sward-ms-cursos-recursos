import pytest
from unittest.mock import AsyncMock
from src.application.use_cases.gestionar_curso import (
    GestionarCursoCommand,
    GestionarCursoUseCase,
)


@pytest.fixture
def use_case():
    repo = AsyncMock()
    repo.save.side_effect = lambda c: c
    repo.find_all.return_value = []
    return GestionarCursoUseCase(repo)


@pytest.mark.asyncio
async def test_crear_curso(use_case):
    cmd = GestionarCursoCommand(nombre="Algoritmos", codigo="CS101")
    c = await use_case.crear(cmd)
    assert c.nombre == "Algoritmos"
    assert c.codigo == "CS101"


@pytest.mark.asyncio
async def test_listar_cursos_vacio(use_case):
    cursos = await use_case.listar()
    assert cursos == []
