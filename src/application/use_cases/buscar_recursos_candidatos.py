from src.domain.entities.recurso_educativo import RecursoEducativo
from src.domain.ports.out_.recurso_repository_port import (
    CriteriosBusqueda,
    RecursoRepositoryPort,
)


class BuscarRecursosCandidatosUseCase:
    def __init__(self, repo: RecursoRepositoryPort):
        self._repo = repo

    async def execute(self, criterios: CriteriosBusqueda) -> list[RecursoEducativo]:
        return await self._repo.find_candidatos(criterios)
