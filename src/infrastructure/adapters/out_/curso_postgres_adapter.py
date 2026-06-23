from uuid import UUID
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sward_shared.identidad import moodle_uuid
from src.domain.entities.actividad import Actividad
from src.domain.entities.curso import Curso, EstadoCurso
from src.application.ports.out_.curso_repository_port import CursoRepositoryPort
from src.infrastructure.db.models.cursos_models import (
    ActividadModel,
    CursoModel,
    RecursoModel,
)


class CursoPostgresAdapter(CursoRepositoryPort):
    def __init__(self, session: AsyncSession):
        self._s = session

    async def find_by_id(self, id: UUID) -> Curso | None:
        r = await self._s.execute(select(CursoModel).where(CursoModel.id == id))
        m = r.scalar_one_or_none()
        return _curso_to_entity(m) if m else None

    async def save(self, curso: Curso) -> Curso:
        r = await self._s.execute(select(CursoModel).where(CursoModel.id == curso.id))
        m = r.scalar_one_or_none()
        if m:
            m.nombre = curso.nombre
            m.codigo = curso.codigo
            m.descripcion = curso.descripcion
            m.estado = curso.estado.value
        else:
            m = CursoModel(
                id=curso.id,
                nombre=curso.nombre,
                codigo=curso.codigo,
                descripcion=curso.descripcion,
                moodle_course_id=curso.moodle_course_id,
                estado=curso.estado.value,
                docente_id=curso.docente_id,
            )
            self._s.add(m)
        await self._s.flush()
        return _curso_to_entity(m)

    async def find_all(self) -> list[Curso]:
        r = await self._s.execute(select(CursoModel))
        return [_curso_to_entity(m) for m in r.scalars().all()]

    async def upsert_by_moodle_id(self, curso: Curso) -> tuple[Curso, bool]:
        """Inserta o actualiza un curso identificándolo por moodle_course_id.

        Idempotente: el sync de Moodle puede correr muchas veces. Devuelve
        (curso, creado) donde ``creado`` es True si fue alta nueva.
        """
        # ID determinístico compartido entre servicios (igual que trazabilidad):
        # uuid5(MOODLE_NS, "course:{moodle_course_id}"). Así el id del catálogo
        # coincide con el curso_id del progreso académico.
        det_id = moodle_uuid("course", curso.moodle_course_id)
        r = await self._s.execute(
            select(CursoModel).where(
                CursoModel.moodle_course_id == curso.moodle_course_id
            )
        )
        m = r.scalar_one_or_none()
        creado = m is None
        # Migra cursos legacy (id uuid4) al id determinístico, reapuntando recursos.
        if m and m.id != det_id:
            await self._s.execute(
                update(RecursoModel)
                .where(RecursoModel.curso_id == m.id)
                .values(curso_id=det_id)
            )
            await self._s.delete(m)
            await self._s.flush()
            m = None
            creado = True
        if m:
            m.nombre = curso.nombre
            if curso.codigo:
                m.codigo = curso.codigo
        else:
            m = CursoModel(
                id=det_id,
                nombre=curso.nombre,
                codigo=curso.codigo,
                descripcion=curso.descripcion,
                moodle_course_id=curso.moodle_course_id,
                estado=curso.estado.value,
                docente_id=curso.docente_id,
            )
            self._s.add(m)
        await self._s.flush()
        return _curso_to_entity(m), creado

    async def find_by_moodle_course_id(self, moodle_course_id: str) -> Curso | None:
        r = await self._s.execute(
            select(CursoModel).where(CursoModel.moodle_course_id == moodle_course_id)
        )
        m = r.scalar_one_or_none()
        return _curso_to_entity(m) if m else None

    async def save_actividad(self, actividad: Actividad) -> Actividad:
        m = ActividadModel(
            id=actividad.id,
            curso_id=actividad.curso_id,
            titulo=actividad.titulo,
            tipo=actividad.tipo,
            puntaje_maximo=actividad.puntaje_maximo,
        )
        self._s.add(m)
        await self._s.flush()
        return actividad

    async def find_actividades(self, curso_id: UUID) -> list[Actividad]:
        r = await self._s.execute(
            select(ActividadModel).where(ActividadModel.curso_id == curso_id)
        )
        return [
            Actividad(
                id=m.id,
                curso_id=m.curso_id,
                titulo=m.titulo,
                tipo=m.tipo,
                puntaje_maximo=m.puntaje_maximo,
            )
            for m in r.scalars().all()
        ]


def _curso_to_entity(m: CursoModel) -> Curso:
    return Curso(
        id=m.id,
        nombre=m.nombre,
        codigo=m.codigo,
        descripcion=m.descripcion,
        moodle_course_id=m.moodle_course_id,
        estado=EstadoCurso(m.estado),
        docente_id=m.docente_id,
    )
