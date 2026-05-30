"""Tests de integración de los endpoints de cursos y recursos (in-process)."""

from uuid import uuid4

import pytest

HEALTH = "/health"
COURSES = "/courses"
RESOURCES = "/resources"
CANDIDATES = "/resources/candidates"


@pytest.mark.asyncio
async def test_health_ok(client):
    resp = await client.get(HEALTH)
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


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
async def test_get_course_inexistente_devuelve_404(client):
    resp = await client.get(f"{COURSES}/{uuid4()}")
    assert resp.status_code == 404
