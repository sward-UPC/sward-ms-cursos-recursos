"""Tipo de módulo de Moodle -> tipo de recurso del catálogo."""

import pytest

from src.application.use_cases.gestionar_recurso import _mapear_tipo_moodle
from src.domain.value_objects.tipo_recurso import TipoRecurso


@pytest.mark.parametrize(
    ("tipo", "esperado"),
    [
        ("video", TipoRecurso.VIDEO),
        ("VIDEO", TipoRecurso.VIDEO),
        ("url", TipoRecurso.LECTURA),
        ("page", TipoRecurso.LECTURA),
        ("quiz", TipoRecurso.QUIZ),
        ("assign", TipoRecurso.EJERCICIO),
        ("", TipoRecurso.EJERCICIO),
    ],
)
def test_mapeo(tipo, esperado):
    assert _mapear_tipo_moodle(tipo) == esperado
