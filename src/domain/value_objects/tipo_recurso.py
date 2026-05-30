from enum import StrEnum


class TipoRecurso(StrEnum):
    VIDEO = "video"
    LECTURA = "lectura"
    EJERCICIO = "ejercicio"
    QUIZ = "quiz"
    PRESENTACION = "presentacion"


class NivelDificultad(StrEnum):
    BASICO = "basico"
    INTERMEDIO = "intermedio"
    AVANZADO = "avanzado"
