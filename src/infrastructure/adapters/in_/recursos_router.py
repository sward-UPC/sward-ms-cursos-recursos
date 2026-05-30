from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from src.application.use_cases.buscar_recursos_candidatos import (
    BuscarRecursosCandidatosUseCase,
)
from src.application.use_cases.gestionar_recurso import (
    GestionarRecursoCommand,
    GestionarRecursoUseCase,
)
from src.domain.ports.out_.recurso_repository_port import CriteriosBusqueda
from src.domain.value_objects.tipo_recurso import NivelDificultad, TipoRecurso
from src.infrastructure.dependencies import (
    get_buscar_candidatos_uc,
    get_gestionar_recurso_uc,
)

router = APIRouter(prefix="/resources", tags=["Recursos"])


class CreateResourceRequest(BaseModel):
    curso_id: UUID
    titulo: str
    tipo: TipoRecurso
    nivel_dificultad: NivelDificultad = NivelDificultad.INTERMEDIO
    url: str = ""
    etiquetas: list[str] = []
    competencia: str = ""
    tiempo_estimado_min: int = 0
    concepto_ids: list[str] = []


@router.post("", status_code=201)
async def create_resource(
    body: CreateResourceRequest,
    uc: GestionarRecursoUseCase = Depends(get_gestionar_recurso_uc),
):
    r = await uc.crear(GestionarRecursoCommand(**body.model_dump()))
    return {"id": str(r.id), "titulo": r.titulo, "tipo": r.tipo}


@router.get("")
async def list_resources(
    curso_id: UUID | None = None,
    uc: GestionarRecursoUseCase = Depends(get_gestionar_recurso_uc),
):
    recursos = await uc.listar(curso_id)
    return [
        {
            "id": str(r.id),
            "titulo": r.titulo,
            "tipo": r.tipo,
            "nivel_dificultad": r.nivel_dificultad,
        }
        for r in recursos
    ]


@router.get("/candidates")
async def get_candidates(
    courseId: UUID | None = None,
    tipo: TipoRecurso | None = None,
    nivel: NivelDificultad | None = None,
    limit: int = 10,
    uc: BuscarRecursosCandidatosUseCase = Depends(get_buscar_candidatos_uc),
):
    recursos = await uc.execute(
        CriteriosBusqueda(
            curso_id=courseId, tipo=tipo, nivel_dificultad=nivel, limit=limit
        )
    )
    return [
        {
            "id": str(r.id),
            "titulo": r.titulo,
            "tipo": r.tipo,
            "nivel_dificultad": r.nivel_dificultad,
            "url": r.url,
        }
        for r in recursos
    ]
