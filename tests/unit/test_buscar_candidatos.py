import pytest
from unittest.mock import AsyncMock
from uuid import uuid4
from src.application.use_cases.buscar_recursos_candidatos import (
    BuscarRecursosCandidatosUseCase,
)
from src.domain.entities.recurso_educativo import RecursoEducativo
from src.application.ports.out_.recurso_repository_port import CriteriosBusqueda
from src.domain.value_objects.tipo_recurso import TipoRecurso


@pytest.mark.asyncio
async def test_buscar_candidatos():
    repo = AsyncMock()
    repo.find_candidatos.return_value = [
        RecursoEducativo(titulo="Video 1", tipo=TipoRecurso.VIDEO),
        RecursoEducativo(titulo="Lectura 1", tipo=TipoRecurso.LECTURA),
    ]
    result = await BuscarRecursosCandidatosUseCase(repo).execute(
        CriteriosBusqueda(curso_id=uuid4())
    )
    assert len(result) == 2


@pytest.mark.asyncio
async def test_buscar_candidatos_vacio():
    repo = AsyncMock()
    repo.find_candidatos.return_value = []
    result = await BuscarRecursosCandidatosUseCase(repo).execute(CriteriosBusqueda())
    assert result == []
