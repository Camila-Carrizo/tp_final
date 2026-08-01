"""
distribuciones.py
-----------------
Funciones que generan números aleatorios del modelo.

  - uniforme / uniforme_entero
  - exponencial
  - direccion_pasajero  → "baja" o "sube"
"""

from __future__ import annotations

import random


def _rng(rng: random.Random | None):
    """Usa el generador indicado o el módulo random global (respeta seed)."""
    return rng if rng is not None else random


def uniforme(a: float, b: float, rng: random.Random | None = None) -> float:
    """Valor continuo uniforme en [a, b]."""
    return _rng(rng).uniform(a, b)


def uniforme_entero(a: int, b: int, rng: random.Random | None = None) -> int:
    """Entero uniforme en [a, b]. Usado para H y P."""
    return _rng(rng).randint(a, b)


def exponencial(media: float, rng: random.Random | None = None) -> float:
    """Tiempo exponencial con la media dada. Usado para L."""
    if media <= 0:
        raise ValueError("La media de la exponencial debe ser > 0.")
    return _rng(rng).expovariate(1.0 / media)


def definir_direccion_pasajero(
    probabilidad_bajar: float = 0.7,
    rng: random.Random | None = None,
) -> str:
    """Devuelve 'baja' o 'sube' (por defecto 70% / 30%)."""
    if not 0.0 <= probabilidad_bajar <= 1.0:
        raise ValueError("probabilidad_bajar debe estar entre 0 y 1.")
    if _rng(rng).random() < probabilidad_bajar:
        return "baja"
    return "sube"
