"""
distribuciones.py
-----------------
Generan (RND, valor) a partir de random() en [0, 1).

Importante: primero se TRUNCA el RND (2 decimales) y ESE valor truncado
es el que entra en la fórmula. El resultado también se trunca.
H y P: RND truncado a 2 → fórmula → entero (0 decimales).
"""

from __future__ import annotations

import math
import random


def truncar(x: float, decimales: int = 2) -> float:
    """Trunca hacia 0 (no redondea)."""
    factor = 10**decimales
    return math.trunc(x * factor) / factor


def _rng(rng: random.Random | None):
    return rng if rng is not None else random


def _rnd_truncado(rng: random.Random | None = None) -> float:
    """
    Genera U(0,1), lo trunca a 2 decimales y devuelve ese truncado.
    random() está en [0, 1) → tras truncar queda en [0.00, 0.99].
    """
    return truncar(_rng(rng).random(), 2)


def uniforme(a: float, b: float, rng: random.Random | None = None) -> tuple[float, float]:
    """
    Continua U(a, b).
    Usa RND ya truncado: valor = a + RND*(b-a), luego trunca el valor.
    """
    rnd = _rnd_truncado(rng)
    valor = truncar(a + rnd * (b - a), 2)
    return rnd, valor


def uniforme_entero(a: int, b: int, rng: random.Random | None = None) -> tuple[float, int]:
    """
    Entero uniforme en [a, b] (H y P).
    Usa RND ya truncado: valor = a + trunc(RND * (b-a+1)).
    """
    if a > b:
        raise ValueError("uniforme_entero: a debe ser <= b")
    rnd = _rnd_truncado(rng)
    valor = a + math.trunc(rnd * (b - a + 1))
    if valor > b:
        valor = b
    return rnd, int(valor)


def exponencial(media: float, rng: random.Random | None = None) -> tuple[float, float]:
    """
    Exponencial con media dada (L).
    Usa RND ya truncado: L = -media * ln(1 - RND), luego trunca L.
    """
    if media <= 0:
        raise ValueError("La media de la exponencial debe ser > 0.")
    rnd = _rnd_truncado(rng)
    # rnd ∈ [0.00, 0.99] → 1-rnd ∈ [0.01, 1.00], ln seguro
    valor = truncar(-media * math.log(1.0 - rnd), 2)
    return rnd, valor


def definir_direccion_pasajero(
    probabilidad_bajar: float = 0.7,
    rng: random.Random | None = None,
) -> tuple[float, str]:
    """Usa RND ya truncado para comparar con la probabilidad."""
    if not 0.0 <= probabilidad_bajar <= 1.0:
        raise ValueError("probabilidad_bajar debe estar entre 0 y 1.")
    rnd = _rnd_truncado(rng)
    if rnd < probabilidad_bajar:
        return rnd, "baja"
    return rnd, "sube"


def campos_aleatorios_vacios() -> dict:
    """Columnas RND / tiempos crudos en None (fila sin ese sorteo)."""
    return {
        "RND_H": None,
        "RND_P": None,
        "RND_LLEGADA_PASAJERO": None,
        "LLEGADA_PASAJERO": None,
        "RND_LLEGADA_ASCENSOR": None,
        "LLEGADA_ASCENSOR": None,
        "RND_DIRECCION_PASAJERO": None,
        "DIRECCION_PASAJERO": None,
    }
