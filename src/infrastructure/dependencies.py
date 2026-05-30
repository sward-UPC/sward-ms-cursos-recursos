from functools import lru_cache

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.use_cases.buscar_recursos_candidatos import (
    BuscarRecursosCandidatosUseCase,
)
from src.application.use_cases.gestionar_curso import GestionarCursoUseCase
from src.application.use_cases.gestionar_recurso import GestionarRecursoUseCase
from src.infrastructure.adapters.out_.curso_postgres_adapter import CursoPostgresAdapter
from src.infrastructure.adapters.out_.eventbridge_adapter import EventBridgeAdapter
from src.infrastructure.adapters.out_.recurso_postgres_adapter import (
    RecursoPostgresAdapter,
)
from src.infrastructure.adapters.out_.s3_adapter import S3Adapter
from src.infrastructure.db.database import get_session


@lru_cache(maxsize=1)
def get_s3_adapter() -> S3Adapter:
    return S3Adapter()


@lru_cache(maxsize=1)
def get_eventbridge_adapter() -> EventBridgeAdapter:
    return EventBridgeAdapter()


def get_gestionar_curso_uc(
    session: AsyncSession = Depends(get_session),
) -> GestionarCursoUseCase:
    return GestionarCursoUseCase(CursoPostgresAdapter(session))


def get_gestionar_recurso_uc(
    session: AsyncSession = Depends(get_session),
    s3: S3Adapter = Depends(get_s3_adapter),
    events: EventBridgeAdapter = Depends(get_eventbridge_adapter),
) -> GestionarRecursoUseCase:
    return GestionarRecursoUseCase(RecursoPostgresAdapter(session), s3, events)


def get_buscar_candidatos_uc(
    session: AsyncSession = Depends(get_session),
) -> BuscarRecursosCandidatosUseCase:
    return BuscarRecursosCandidatosUseCase(RecursoPostgresAdapter(session))
