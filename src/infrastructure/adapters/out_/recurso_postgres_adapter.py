from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.entities.metadata_recurso import MetadataRecurso
from src.domain.entities.recurso_educativo import RecursoEducativo
from src.domain.ports.out_.recurso_repository_port import (
    CriteriosBusqueda,
    RecursoRepositoryPort,
)
from src.domain.value_objects.tipo_recurso import NivelDificultad, TipoRecurso
from src.infrastructure.db.models.cursos_models import (
    MetadataRecursoModel,
    RecursoModel,
)


class RecursoPostgresAdapter(RecursoRepositoryPort):
    def __init__(self, session: AsyncSession):
        self._s = session

    async def save(
        self, recurso: RecursoEducativo, metadata: MetadataRecurso | None = None
    ) -> RecursoEducativo:
        m = RecursoModel(
            id=recurso.id,
            curso_id=recurso.curso_id,
            titulo=recurso.titulo,
            tipo=recurso.tipo.value,
            nivel_dificultad=recurso.nivel_dificultad.value,
            url=recurso.url,
            s3_key=recurso.s3_key,
            activo=recurso.activo,
        )
        self._s.add(m)
        if metadata:
            self._s.add(
                MetadataRecursoModel(
                    id=metadata.id,
                    recurso_id=recurso.id,
                    competencia=metadata.competencia,
                    tiempo_estimado_min=metadata.tiempo_estimado_min,
                )
            )
        await self._s.flush()
        return recurso

    async def find_by_id(self, id: UUID) -> RecursoEducativo | None:
        r = await self._s.execute(select(RecursoModel).where(RecursoModel.id == id))
        m = r.scalar_one_or_none()
        return _to_entity(m) if m else None

    async def find_candidatos(
        self, criterios: CriteriosBusqueda
    ) -> list[RecursoEducativo]:
        q = select(RecursoModel).where(RecursoModel.activo == True)  # noqa: E712
        if criterios.curso_id:
            q = q.where(RecursoModel.curso_id == criterios.curso_id)
        if criterios.tipo:
            q = q.where(RecursoModel.tipo == criterios.tipo.value)
        if criterios.nivel_dificultad:
            q = q.where(
                RecursoModel.nivel_dificultad == criterios.nivel_dificultad.value
            )
        q = q.limit(criterios.limit)
        r = await self._s.execute(q)
        return [_to_entity(m) for m in r.scalars().all()]

    async def find_all(self, curso_id: UUID | None = None) -> list[RecursoEducativo]:
        q = select(RecursoModel)
        if curso_id:
            q = q.where(RecursoModel.curso_id == curso_id)
        r = await self._s.execute(q)
        return [_to_entity(m) for m in r.scalars().all()]

    async def upsert_by_moodle_id(
        self, recurso: RecursoEducativo
    ) -> tuple[RecursoEducativo, bool]:
        """Inserta o actualiza un recurso identificándolo por moodle_resource_id.

        Idempotente: el sync de actividades de Moodle puede correr muchas veces.
        Devuelve (recurso, creado) donde ``creado`` es True si fue alta nueva.
        """
        r = await self._s.execute(
            select(RecursoModel).where(
                RecursoModel.moodle_resource_id == recurso.moodle_resource_id
            )
        )
        m = r.scalar_one_or_none()
        creado = m is None
        if m:
            m.titulo = recurso.titulo
            m.tipo = recurso.tipo.value
            m.curso_id = recurso.curso_id
        else:
            m = RecursoModel(
                id=recurso.id,
                curso_id=recurso.curso_id,
                titulo=recurso.titulo,
                tipo=recurso.tipo.value,
                nivel_dificultad=recurso.nivel_dificultad.value,
                url=recurso.url,
                s3_key=recurso.s3_key,
                activo=recurso.activo,
                moodle_resource_id=recurso.moodle_resource_id,
            )
            self._s.add(m)
        await self._s.flush()
        return _to_entity(m), creado


def _to_entity(m: RecursoModel) -> RecursoEducativo:
    return RecursoEducativo(
        id=m.id,
        curso_id=m.curso_id,
        titulo=m.titulo,
        tipo=TipoRecurso(m.tipo),
        nivel_dificultad=NivelDificultad(m.nivel_dificultad),
        url=m.url,
        s3_key=m.s3_key,
        activo=m.activo,
        moodle_resource_id=m.moodle_resource_id,
    )
