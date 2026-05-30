from dataclasses import dataclass
from uuid import UUID
from src.domain.entities.curso import Curso
from src.domain.ports.out_.curso_repository_port import CursoRepositoryPort


@dataclass
class GestionarCursoCommand:
    nombre: str
    codigo: str
    descripcion: str = ""
    moodle_course_id: str = ""
    docente_id: UUID | None = None


class GestionarCursoUseCase:
    def __init__(self, repo: CursoRepositoryPort):
        self._repo = repo

    async def crear(self, cmd: GestionarCursoCommand) -> Curso:
        curso = Curso(
            nombre=cmd.nombre,
            codigo=cmd.codigo,
            descripcion=cmd.descripcion,
            moodle_course_id=cmd.moodle_course_id,
            docente_id=cmd.docente_id,
        )
        return await self._repo.save(curso)

    async def listar(self) -> list[Curso]:
        return await self._repo.find_all()

    async def obtener(self, id: UUID) -> Curso | None:
        return await self._repo.find_by_id(id)
