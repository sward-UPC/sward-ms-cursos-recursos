import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from src.application.use_cases.gestionar_recurso import (
    GestionarRecursoCommand,
    GestionarRecursoUseCase,
)
from src.domain.value_objects.tipo_recurso import TipoRecurso


@pytest.fixture
def use_case():
    repo = AsyncMock()
    repo.save.side_effect = lambda r, m=None: r
    return GestionarRecursoUseCase(repo, AsyncMock(), MagicMock())


@pytest.mark.asyncio
async def test_crear_recurso(use_case):
    cmd = GestionarRecursoCommand(
        curso_id=uuid4(), titulo="Intro a Algoritmos", tipo=TipoRecurso.VIDEO
    )
    r = await use_case.crear(cmd)
    assert r.titulo == "Intro a Algoritmos"
    assert r.tipo == TipoRecurso.VIDEO


@pytest.mark.asyncio
async def test_crear_publica_evento(use_case):
    cmd = GestionarRecursoCommand(
        curso_id=uuid4(), titulo="Quiz 1", tipo=TipoRecurso.QUIZ
    )
    await use_case.crear(cmd)
    use_case._event_publisher.publish.assert_called_once()
