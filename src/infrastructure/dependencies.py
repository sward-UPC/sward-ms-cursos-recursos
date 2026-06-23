from functools import lru_cache

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sward_shared.auth import build_require_jwt, build_require_service_key

from src.application.use_cases.buscar_recursos_candidatos import (
    BuscarRecursosCandidatosUseCase,
)
from src.application.use_cases.gestionar_curso import GestionarCursoUseCase
from src.application.use_cases.gestionar_recurso import (
    GestionarRecursoUseCase,
    SincronizarRecursosUseCase,
)
from src.infrastructure.adapters.out_.curso_postgres_adapter import CursoPostgresAdapter
from src.infrastructure.adapters.out_.eventbridge_adapter import EventBridgeAdapter
from src.infrastructure.adapters.out_.recurso_postgres_adapter import (
    RecursoPostgresAdapter,
)
from src.infrastructure.adapters.out_.s3_adapter import S3Adapter
from src.infrastructure.config.settings import settings
from src.infrastructure.db.database import get_session

# Dependencia de autenticación JWT reutilizable, compartida vía sward-shared.
require_jwt = build_require_jwt(settings.secret_key, algorithm=settings.jwt_algorithm)

# Validación entrante de service-key (modo dev permite sin claves configuradas).
require_service_key = build_require_service_key(settings.authorized_service_keys_set)


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


def get_sincronizar_recursos_uc(
    session: AsyncSession = Depends(get_session),
) -> SincronizarRecursosUseCase:
    return SincronizarRecursosUseCase(
        RecursoPostgresAdapter(session), CursoPostgresAdapter(session)
    )
