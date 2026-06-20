"""Tests de integración de los endpoints de cursos y recursos (in-process)."""

from uuid import uuid4

import pytest

HEALTH = "/health"
COURSES = "/courses"
RESOURCES = "/resources"
CANDIDATES = "/resources/candidates"
COURSES_SYNC = "/internal/courses/sync"
RESOURCES_SYNC = "/internal/resources/sync"


@pytest.mark.asyncio
async def test_health_ok(client):
    resp = await client.get(HEALTH)
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_endpoint_protegido_sin_token_retorna_401(anon_client):
    resp = await anon_client.get(COURSES)
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_crear_curso_devuelve_201(client):
    resp = await client.post(COURSES, json={"nombre": "Cálculo I", "codigo": "MA101"})
    assert resp.status_code == 201
    body = resp.json()
    assert body["nombre"] == "Cálculo I"
    assert body["codigo"] == "MA101"
    assert "id" in body


@pytest.mark.asyncio
async def test_flujo_crear_curso_luego_listar(client):
    await client.post(COURSES, json={"nombre": "Física I", "codigo": "FI101"})

    resp = await client.get(COURSES)
    assert resp.status_code == 200
    cursos = resp.json()
    assert len(cursos) == 1
    assert cursos[0]["codigo"] == "FI101"
    assert cursos[0]["estado"] == "activo"


@pytest.mark.asyncio
async def test_editar_curso_descripcion_y_estado(client):
    creado = (
        await client.post(COURSES, json={"nombre": "Redes", "codigo": "RD101"})
    ).json()

    resp = await client.put(
        f"{COURSES}/{creado['id']}",
        json={"descripcion": "Curso de redes neuronales", "estado": "inactivo"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["descripcion"] == "Curso de redes neuronales"
    assert body["estado"] == "inactivo"
    # nombre/codigo no cambian
    assert body["nombre"] == "Redes"
    assert body["codigo"] == "RD101"


@pytest.mark.asyncio
async def test_editar_curso_inexistente_devuelve_404(client):
    import uuid

    resp = await client.put(f"{COURSES}/{uuid.uuid4()}", json={"estado": "inactivo"})
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_flujo_crear_recurso_luego_candidates(client):
    curso = await client.post(
        COURSES, json={"nombre": "Programación", "codigo": "CS100"}
    )
    curso_id = curso.json()["id"]

    rec = await client.post(
        RESOURCES,
        json={
            "curso_id": curso_id,
            "titulo": "Intro a Python",
            "tipo": "video",
            "nivel_dificultad": "basico",
            "url": "https://ejemplo/video",
        },
    )
    assert rec.status_code == 201
    assert rec.json()["titulo"] == "Intro a Python"

    resp = await client.get(CANDIDATES, params={"courseId": curso_id})
    assert resp.status_code == 200
    candidatos = resp.json()
    assert len(candidatos) == 1
    assert candidatos[0]["tipo"] == "video"
    assert candidatos[0]["nivel_dificultad"] == "basico"


@pytest.mark.asyncio
async def test_candidates_filtra_por_tipo(client):
    curso = await client.post(COURSES, json={"nombre": "X", "codigo": "X1"})
    curso_id = curso.json()["id"]

    await client.post(
        RESOURCES,
        json={"curso_id": curso_id, "titulo": "Vid", "tipo": "video"},
    )
    await client.post(
        RESOURCES,
        json={"curso_id": curso_id, "titulo": "Quiz", "tipo": "quiz"},
    )

    resp = await client.get(CANDIDATES, params={"courseId": curso_id, "tipo": "quiz"})
    assert resp.status_code == 200
    candidatos = resp.json()
    assert len(candidatos) == 1
    assert candidatos[0]["tipo"] == "quiz"


@pytest.mark.asyncio
async def test_sync_propaga_url_seccion_y_candidates_filtra_por_seccion(client):
    await client.post(
        COURSES_SYNC,
        json={"cursos": [{"moodle_course_id": "10", "nombre": "Algoritmos"}]},
    )
    await client.post(
        RESOURCES_SYNC,
        json={
            "recursos": [
                {
                    "moodle_activity_id": "10-act-1",
                    "moodle_course_id": "10",
                    "titulo": "Quiz de ordenamiento",
                    "tipo": "quiz",
                    "url": "https://moodle/mod/quiz/view.php?id=1",
                    "seccion": "ordenamiento",
                },
                {
                    "moodle_activity_id": "10-act-2",
                    "moodle_course_id": "10",
                    "titulo": "Lectura de grafos",
                    "tipo": "page",
                    "url": "https://moodle/mod/page/view.php?id=2",
                    "seccion": "grafos",
                },
            ]
        },
    )

    # candidates expone url y seccion.
    todos = await client.get(CANDIDATES)
    assert todos.status_code == 200
    por_titulo = {c["titulo"]: c for c in todos.json()}
    quiz = por_titulo["Quiz de ordenamiento"]
    assert quiz["url"] == "https://moodle/mod/quiz/view.php?id=1"
    assert quiz["seccion"] == "ordenamiento"

    # El filtro por seccion restringe los candidatos a ese concepto.
    filtrados = await client.get(CANDIDATES, params={"seccion": "grafos"})
    assert filtrados.status_code == 200
    candidatos = filtrados.json()
    assert len(candidatos) == 1
    assert candidatos[0]["titulo"] == "Lectura de grafos"
    assert candidatos[0]["seccion"] == "grafos"


@pytest.mark.asyncio
async def test_get_course_inexistente_devuelve_404(client):
    resp = await client.get(f"{COURSES}/{uuid4()}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_sync_recursos_crea_y_resuelve_curso(client):
    # El curso debe existir para resolver el curso_id interno.
    await client.post(
        COURSES_SYNC,
        json={"cursos": [{"moodle_course_id": "10", "nombre": "Algoritmos"}]},
    )

    resp = await client.post(
        RESOURCES_SYNC,
        json={
            "recursos": [
                {
                    "moodle_activity_id": "10-act-1",
                    "moodle_course_id": "10",
                    "titulo": "Quiz de ordenamiento",
                    "tipo": "quiz",
                }
            ]
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body == {"procesados": 1, "creados": 1, "actualizados": 0, "omitidos": 0}

    # El recurso queda asociado al curso resuelto y aparece en candidates.
    listado = await client.get(RESOURCES)
    recursos = listado.json()
    assert len(recursos) == 1
    assert recursos[0]["titulo"] == "Quiz de ordenamiento"
    assert recursos[0]["tipo"] == "quiz"


@pytest.mark.asyncio
async def test_sync_recursos_es_idempotente(client):
    await client.post(
        COURSES_SYNC,
        json={"cursos": [{"moodle_course_id": "10", "nombre": "Algoritmos"}]},
    )
    payload = {
        "recursos": [
            {
                "moodle_activity_id": "10-act-1",
                "moodle_course_id": "10",
                "titulo": "Tarea 1",
                "tipo": "assign",
            }
        ]
    }
    await client.post(RESOURCES_SYNC, json=payload)
    resp = await client.post(RESOURCES_SYNC, json=payload)
    assert resp.json() == {
        "procesados": 1,
        "creados": 0,
        "actualizados": 1,
        "omitidos": 0,
    }
    listado = await client.get(RESOURCES)
    assert len(listado.json()) == 1


@pytest.mark.asyncio
async def test_sync_recursos_omite_curso_inexistente(client):
    resp = await client.post(
        RESOURCES_SYNC,
        json={
            "recursos": [
                {
                    "moodle_activity_id": "99-act-1",
                    "moodle_course_id": "99",
                    "titulo": "Huérfano",
                    "tipo": "page",
                }
            ]
        },
    )
    assert resp.status_code == 200
    assert resp.json() == {
        "procesados": 1,
        "creados": 0,
        "actualizados": 0,
        "omitidos": 1,
    }
