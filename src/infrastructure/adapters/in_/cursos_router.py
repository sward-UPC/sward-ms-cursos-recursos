from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from src.application.use_cases.gestionar_curso import (
    GestionarCursoCommand,
    GestionarCursoUseCase,
)
from src.infrastructure.adapters.out_.curso_postgres_adapter import CursoPostgresAdapter
from src.infrastructure.db.database import get_session

router = APIRouter(prefix="/courses", tags=["Cursos"])


class CreateCourseRequest(BaseModel):
    nombre: str
    codigo: str
    descripcion: str = ""
    moodle_course_id: str = ""


@router.post("", status_code=201)
async def create_course(
    body: CreateCourseRequest, session: AsyncSession = Depends(get_session)
):
    uc = GestionarCursoUseCase(CursoPostgresAdapter(session))
    c = await uc.crear(GestionarCursoCommand(**body.model_dump()))
    return {"id": str(c.id), "nombre": c.nombre, "codigo": c.codigo}


@router.get("")
async def list_courses(session: AsyncSession = Depends(get_session)):
    uc = GestionarCursoUseCase(CursoPostgresAdapter(session))
    cursos = await uc.listar()
    return [
        {"id": str(c.id), "nombre": c.nombre, "codigo": c.codigo, "estado": c.estado}
        for c in cursos
    ]


@router.get("/{course_id}")
async def get_course(course_id: UUID, session: AsyncSession = Depends(get_session)):
    uc = GestionarCursoUseCase(CursoPostgresAdapter(session))
    c = await uc.obtener(course_id)
    if not c:
        raise HTTPException(404, "Curso no encontrado")
    return {"id": str(c.id), "nombre": c.nombre, "codigo": c.codigo}
