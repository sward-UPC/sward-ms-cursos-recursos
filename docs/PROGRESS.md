# PROGRESS — sward-ms-cursos-recursos

## Sprint 4 — 2026-05-29

### Implementado
- [x] Entidades: Curso, Actividad, RecursoEducativo, MetadataRecurso
- [x] Value objects: TipoRecurso, NivelDificultad
- [x] Evento: RecursoActualizadoEvent
- [x] Use Cases: GestionarCurso, GestionarRecurso, BuscarRecursosCandidatos
- [x] CursoPostgresAdapter, RecursoPostgresAdapter
- [x] S3Adapter (mock en dev), EventBridgeAdapter
- [x] Endpoints: GET/POST /courses, GET/POST /resources, GET /resources/candidates
- [x] SQLAlchemy models: courses, activities, resources, resource_metadata
- [x] Docker Compose: PostgreSQL 15
- [x] Tests unitarios: 5 tests
- [x] GitHub Actions CI
