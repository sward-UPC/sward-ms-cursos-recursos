from uuid import uuid4
from sqlalchemy import Boolean, Float, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class CursoModel(Base):
    __tablename__ = "courses"
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    codigo: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    descripcion: Mapped[str] = mapped_column(String(1000), default="")
    moodle_course_id: Mapped[str] = mapped_column(String(100), default="", index=True)
    estado: Mapped[str] = mapped_column(String(50), default="activo")
    docente_id: Mapped[UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)


class ActividadModel(Base):
    __tablename__ = "activities"
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    curso_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True
    )
    titulo: Mapped[str] = mapped_column(String(255), nullable=False)
    tipo: Mapped[str] = mapped_column(String(50), default="")
    puntaje_maximo: Mapped[float] = mapped_column(Float, default=100.0)
    moodle_activity_id: Mapped[str] = mapped_column(String(100), default="")


class RecursoModel(Base):
    __tablename__ = "resources"
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    curso_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True
    )
    titulo: Mapped[str] = mapped_column(String(255), nullable=False)
    tipo: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    nivel_dificultad: Mapped[str] = mapped_column(
        String(50), default="intermedio", index=True
    )
    url: Mapped[str] = mapped_column(String(500), default="")
    s3_key: Mapped[str] = mapped_column(String(500), default="")
    activo: Mapped[bool] = mapped_column(Boolean, default=True)


class MetadataRecursoModel(Base):
    __tablename__ = "resource_metadata"
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    recurso_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, unique=True, index=True
    )
    competencia: Mapped[str] = mapped_column(String(255), default="")
    tiempo_estimado_min: Mapped[int] = mapped_column(Integer, default=0)
