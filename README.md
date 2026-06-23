# sward-ms-cursos-recursos

Microservicio de **catálogo de cursos y recursos educativos** de la plataforma
**SWARD**. Administra cursos, sus actividades y los recursos educativos asociados, y
expone los **recursos candidatos** que consume el motor de recomendación mediante un
endpoint servicio-a-servicio.

Construido con **FastAPI** siguiendo **arquitectura hexagonal (Ports & Adapters)** con
toques de DDD.

---

## ¿Qué hace?

- **Gestión de cursos:** alta, listado, consulta por ID y edición (descripción/estado)
  del catálogo de cursos.
- **Gestión de recursos:** alta y listado de recursos educativos (video, lectura,
  ejercicio, quiz, presentación) con su metadata (etiquetas, competencia, tiempo
  estimado, conceptos).
- **Candidatos a recomendar:** endpoint s2s que devuelve recursos filtrados por curso,
  tipo, nivel de dificultad y sección/concepto, paginado. Lo consume
  `sward-ms-recomendacion`.
- **Sincronización desde Moodle:** endpoints internos s2s para que
  `sward-ms-integracion-lms` propague cursos y actividades de Moodle al catálogo
  (upsert idempotente por ID de Moodle).
- **Eventos de dominio:** publica `RecursoActualizado` a EventBridge al crear/actualizar
  recursos (en desarrollo se loguea, no se emite).

---

## Stack

- **Python 3.11** · **FastAPI** · **Uvicorn**
- **SQLAlchemy 2.0** (async, `asyncpg`) · **PostgreSQL 15**
- **Pydantic v2** / **pydantic-settings** (configuración por entorno)
- **boto3** — AWS S3 (URLs presignadas de recursos) y EventBridge (eventos de dominio)
- **scalar-fastapi** — referencia de API interactiva (`/scalar`)
- **sward-shared** — librería compartida (auth JWT/service-key, eventos de dominio,
  identidad determinística de Moodle)
- Auth: **JWT HS256** (usuario final) + **X-Service-Key** (servicio-a-servicio)

---

## Estructura hexagonal

Nomenclatura del repo: `domain` (núcleo) · `application/use_cases` · `infrastructure/
adapters/{in_,out_}` · `infrastructure/config`. Las dependencias apuntan hacia adentro:
el dominio no conoce frameworks; la infraestructura implementa los puertos del dominio.

```
src/
  domain/                              # NÚCLEO — sin frameworks
    entities/
      curso.py                         # Curso, EstadoCurso
      actividad.py                     # Actividad
      recurso_educativo.py             # RecursoEducativo
      metadata_recurso.py              # MetadataRecurso
    value_objects/
      tipo_recurso.py                  # TipoRecurso, NivelDificultad (StrEnum)
    events/
      recurso_actualizado_event.py     # RecursoActualizadoEvent (evento de dominio)
    ports/
      out_/                            # CONTRATOS (ABC) que la app necesita del exterior
        curso_repository_port.py
        recurso_repository_port.py     # + CriteriosBusqueda
        event_publisher_port.py
        storage_port.py

  application/
    use_cases/                         # CASOS DE USO — orquestan, tipan contra puertos
      gestionar_curso.py               # GestionarCursoUseCase (+ comandos, error de dominio)
      gestionar_recurso.py             # GestionarRecursoUseCase
      buscar_recursos_candidatos.py    # BuscarRecursosCandidatosUseCase

  infrastructure/
    adapters/
      in_/                             # ADAPTADORES DE ENTRADA (driving) — FastAPI
        main.py                        # app, lifespan, CORS, headers, handler global
        cursos_router.py               # /courses (+ /internal/courses/sync)
        recursos_router.py             # /resources, /resources/candidates (+ /internal/resources/sync)
      out_/                            # ADAPTADORES DE SALIDA (driven) — implementan ports/
        curso_postgres_adapter.py
        recurso_postgres_adapter.py
        s3_adapter.py                  # StoragePort (mock en dev)
        eventbridge_adapter.py         # EventPublisherPort (log en dev)
    config/
      settings.py                      # pydantic-settings (env)
    db/
      database.py                      # engine async + get_session
      models/cursos_models.py          # modelos ORM (courses, activities, resources, resource_metadata)
    dependencies.py                    # COMPOSITION ROOT — cablea puertos↔implementaciones (Depends)

tests/
  unit/                                # casos de uso con fakes en memoria
  integration/                         # endpoints (httpx + app), docs Scalar
```

> Auditoría de cumplimiento del patrón en [`AUDIT_HEXAGONAL.md`](./AUDIT_HEXAGONAL.md).

---

## Endpoints

### Cursos (`/courses`) — Auth: JWT

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/courses` | Crea un curso |
| `GET` | `/courses` | Lista todos los cursos |
| `GET` | `/courses/{course_id}` | Detalle de un curso |
| `PUT` | `/courses/{course_id}` | Edita descripción/estado (no toca campos de Moodle) |

### Recursos (`/resources`) — Auth: JWT

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/resources` | Crea un recurso educativo |
| `GET` | `/resources?curso_id=` | Lista recursos (opcionalmente por curso) |

### Candidatos a recomendar — Auth: **X-Service-Key**

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/resources/candidates` | Recursos candidatos para recomendación (s2s) |

Query params: `courseId` (UUID), `tipo` (`video|lectura|ejercicio|quiz|presentacion`),
`nivel` (`basico|intermedio|avanzado`), `seccion` (string), `limit` (1–100, default 10).
Devuelve `id, titulo, tipo, nivel_dificultad, url, seccion`. Lo consume
`sward-ms-recomendacion`; se valida con la cabecera `X-Service-Key` (en desarrollo, sin
claves configuradas, no bloquea).

### Sincronización interna desde Moodle — Auth: **X-Service-Key**

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/internal/courses/sync` | Upsert idempotente de cursos (por `moodle_course_id`) |
| `POST` | `/internal/resources/sync` | Upsert idempotente de recursos (por `moodle_activity_id`) |

Consumidos por `sward-ms-integracion-lms`. El sync de cursos corre antes que el de
recursos (este resuelve el `curso_id` interno por `moodle_course_id`).

### Operación

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/health` | Liveness/readiness |
| `GET` | `/scalar` | Referencia de API interactiva (Scalar) |
| `GET` | `/courses/openapi.json` | Esquema OpenAPI |

---

## Variables de entorno

Configuradas vía `pydantic-settings` (archivo `.env` o variables de entorno). Ver
[`.env.example`](./.env.example).

| Variable | Default | Descripción |
|---|---|---|
| `DATABASE_URL` | `postgresql+asyncpg://sward:sward@localhost:5432/cursos_recursos_db` | URL de conexión async a Postgres |
| `DB_USERNAME` / `DB_PASSWORD` / `DATABASE_HOST` / `DATABASE_PORT` / `DATABASE_NAME` | `""` | Componentes inyectados por la task de ECS (Secrets Manager); si están presentes, **componen** `DATABASE_URL` |
| `ENVIRONMENT` | `development` | `development` activa mocks (S3/EventBridge) y relaja validaciones |
| `SERVICE_NAME` | `sward-ms-cursos-recursos` | Nombre del servicio |
| `AWS_REGION` | `us-east-1` | Región AWS |
| `AWS_S3_BUCKET` | `sward-recursos-educativos` | Bucket de recursos educativos |
| `EVENTBRIDGE_BUS_NAME` | `sward-event-bus` | Event bus de EventBridge |
| `LMS_SERVICE_URL` | `http://localhost:8002` | URL de `ms-integracion-lms` |
| `CORS_ALLOWED_ORIGINS` | `["http://localhost:5173"]` | Orígenes CORS permitidos |
| `SECRET_KEY` | `dev-secret-change-in-production` | Secreto JWT (HS256). **Obligatorio** cambiarlo fuera de desarrollo |
| `JWT_ALGORITHM` | `HS256` | Algoritmo del JWT |
| `SERVICE_KEY` | `""` | Clave propia que este servicio envía en llamadas salientes |
| `AUTHORIZED_SERVICE_KEYS` | `""` | Claves entrantes autorizadas, separadas por coma (legacy/manual) |
| `AUTHORIZED_RECOMENDACION_KEY` | `""` | Clave del caller `ms-recomendacion` (Secrets Manager) |
| `AUTHORIZED_INTEGRACION_LMS_KEY` | `""` | Clave del caller `ms-integracion-lms` (Secrets Manager) |

---

## Correr en local

```bash
# 1. Dependencias
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt

# 2. Configuración
cp .env.example .env

# 3. Base de datos (PostgreSQL en Docker — expuesta en el puerto 5435)
docker compose up -d db

# 4. Servicio (las tablas se crean/migran al arrancar, vía lifespan)
uvicorn src.infrastructure.adapters.in_.main:app --reload --port 8004
```

API: http://localhost:8004 · Docs interactivas: http://localhost:8004/scalar

Alternativa con todo en Docker:

```bash
docker compose up --build      # app en :8004, db en :5435
```

> Nota: el esquema se crea con `Base.metadata.create_all` + migraciones ligeras
> idempotentes (`ADD COLUMN IF NOT EXISTS`) ejecutadas en el arranque; no se requiere
> un paso de migración manual.

## Tests

```bash
pytest -q                      # suite completa (unit + integration)
pytest tests/unit -q           # solo casos de uso (fakes en memoria, sin I/O)
pytest --cov=src               # con cobertura
ruff check                     # linting
```

Los tests de integración ejercen la app FastAPI in-process (`httpx.AsyncClient` +
`ASGITransport`) sustituyendo los repositorios por fakes en memoria vía
`dependency_overrides`; no requieren Postgres real.

---

## Flujo de deploy

CI/CD con GitHub Actions (workflows reutilizables de la organización `sward-UPC`):

1. **CI** (`.github/workflows/ci.yml`): en cada `push`/`pull_request` a `main` corre
   tests y linting (`ci-microservice.yml@main`, con `needs_shared: true` para instalar
   `sward-shared`).
2. **Build & Push** (`.github/workflows/build-push.yml`): un `push` a la rama **`deploy`**
   construye la imagen Docker, la publica en **GHCR** (`sward-ms-cursos-recursos`) y
   dispara el redeploy del servicio **ECS Fargate** (`cursos-recursos` en el cluster
   `sward-cluster`) vía `build-push-ghcr.yml@main`.

Resumen del flujo: `merge a main` → CI verde → `push a deploy` → imagen a GHCR →
actualización del servicio ECS.

---

## Proyecto

**TP202610051** — Universidad Peruana de Ciencias Aplicadas (UPC)
Taller de Proyecto · 2026
