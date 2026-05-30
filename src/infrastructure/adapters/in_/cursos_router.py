from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field

from src.application.use_cases.gestionar_curso import (
    GestionarCursoCommand,
    GestionarCursoUseCase,
)
from src.infrastructure.dependencies import get_gestionar_curso_uc, require_jwt

# Todos los endpoints de /courses exigen un JWT de acceso válido.
router = APIRouter(
    prefix="/courses", tags=["Cursos"], dependencies=[Depends(require_jwt)]
)


class CreateCourseRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nombre: str = Field(max_length=255)
    codigo: str = Field(max_length=64)
    descripcion: str = Field(default="", max_length=2000)
    moodle_course_id: str = Field(default="", max_length=64)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_course(
    body: CreateCourseRequest,
    uc: GestionarCursoUseCase = Depends(get_gestionar_curso_uc),
):
    c = await uc.crear(GestionarCursoCommand(**body.model_dump()))
    return {"id": str(c.id), "nombre": c.nombre, "codigo": c.codigo}


@router.get("")
async def list_courses(uc: GestionarCursoUseCase = Depends(get_gestionar_curso_uc)):
    cursos = await uc.listar()
    return [
        {"id": str(c.id), "nombre": c.nombre, "codigo": c.codigo, "estado": c.estado}
        for c in cursos
    ]


@router.get("/{course_id}")
async def get_course(
    course_id: UUID,
    uc: GestionarCursoUseCase = Depends(get_gestionar_curso_uc),
):
    c = await uc.obtener(course_id)
    if not c:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Curso no encontrado"
        )
    return {"id": str(c.id), "nombre": c.nombre, "codigo": c.codigo}
