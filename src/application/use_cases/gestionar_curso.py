from dataclasses import dataclass
from uuid import UUID
from src.domain.entities.curso import Curso, EstadoCurso
from src.domain.ports.out_.curso_repository_port import CursoRepositoryPort


class CursoNoEncontradoError(Exception):
    """El curso solicitado no existe."""


@dataclass
class GestionarCursoCommand:
    nombre: str
    codigo: str
    descripcion: str = ""
    moodle_course_id: str = ""
    docente_id: UUID | None = None


@dataclass
class ActualizarCursoCommand:
    """Campos editables desde el panel admin (los que el sync de Moodle no pisa)."""

    descripcion: str | None = None
    estado: EstadoCurso | None = None


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

    async def actualizar(self, id: UUID, cmd: ActualizarCursoCommand) -> Curso:
        curso = await self._repo.find_by_id(id)
        if curso is None:
            raise CursoNoEncontradoError(str(id))
        if cmd.descripcion is not None:
            curso.descripcion = cmd.descripcion
        if cmd.estado is not None:
            curso.estado = cmd.estado
        return await self._repo.save(curso)
