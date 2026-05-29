# sward-ms-cursos-recursos

Microservicio de gestión de cursos y recursos educativos del sistema **SWARD**.  
Administra el catálogo de cursos, actividades y recursos educativos, con almacenamiento de archivos en AWS S3.

## Arquitectura

Arquitectura **Hexagonal (Ports & Adapters)**:

```
src/
  domain/           # Curso, Actividad, RecursoEducativo, MetadataRecurso
  application/      # GestionarCursoUseCase, GestionarRecursoUseCase, BuscarRecursosCandidatosUseCase
  infrastructure/   # FastAPI routers, CursoPostgresAdapter, S3Adapter, IntegracionLmsRestAdapter
```

## Stack

- Python 3.11 · FastAPI · SQLAlchemy 2.0 · Alembic · PostgreSQL
- boto3 (S3 + EventBridge) · httpx · Pydantic v2

## Desarrollo local

```bash
cp .env.example .env
docker compose up -d db
alembic upgrade head
uvicorn src.infrastructure.adapters.in_.main:app --reload --port 8004
```

## Tests

```bash
pytest tests/ -v --cov=src
```

## Endpoints principales

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/courses` | Listar cursos |
| GET | `/courses/{id}/activities` | Actividades del curso |
| GET | `/resources/candidates` | Recursos candidatos para recomendación |
| POST | `/resources` | Registrar recurso educativo |

## Proyecto

**TP202610051** — Universidad Peruana de Ciencias Aplicadas (UPC)  
Taller de Proyecto 1 / 2026
