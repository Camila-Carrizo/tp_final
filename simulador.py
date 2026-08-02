"""
simulador.py
------------
Acá se va a hacer la simulación.

Solo guardamos 2 filas en memoria:
  - estado_anterior: la de arriba
  - estado_actual: la que estamos armando

Si se indica ruta_excel, cada fila se escribe al .xlsx (append)
y al final se guarda el archivo para que la UI lo abra.
"""

from __future__ import annotations

import random
from pathlib import Path

from parametros import crear_parametros
from distribuciones import (
    uniforme,
    uniforme_entero,
    exponencial,
    truncar,
    campos_aleatorios_vacios,
)
from excel import EscritorExcel
from utils.utils_llegada_ascensor import simular_llegada_ascensor
from utils.utils_llegada_pasajeros import simular_llegada_pasajero
from utils.utils_fin_descenso import simular_fin_descenso
from utils.utils_fin_ascenso import simular_fin_ascenso
from utils.utils_fin_espera import simular_fin_espera


def ejecutar(parametros: dict | None = None, ruta_excel: str | Path | None = None):
    """
    Corre la simulación.
    - parametros: si es None, usa crear_parametros().
    - ruta_excel: si se indica, escribe cada fila al archivo y lo guarda.
    Devuelve: (estado_final, ruta_del_excel | None)
    """
    if parametros is None:
        parametros = crear_parametros()

    if parametros["semilla"] is not None:
        random.seed(parametros["semilla"])

    escritor = EscritorExcel(ruta_excel) if ruta_excel else None

    estado_anterior = {}
    estado_actual = armar_estado_inicial(parametros)
    cantidad_eventos = parametros["cantidad_eventos"]

    for i in range(cantidad_eventos):
        if i == 0:
            estado_actual = armar_estado_inicial(parametros)
        else:
            estado_anterior = estado_actual
            estado_actual = armar_estado_actual(estado_anterior, parametros)

        if escritor is not None:
            escritor.agregar_fila(estado_actual)

    ruta_guardada = None
    if escritor is not None:
        escritor.escribir_parametros(parametros)
        ruta_guardada = escritor.guardar()

    return estado_actual, ruta_guardada

def determinar_proximo_evento(estado_actual):
    """
    Mira los tiempos programados y elige el más chico (el que ocurre primero).
    Ignora los que están en None.
    Devuelve: (nombre_del_campo, tiempo_de_reloj)
    """
    candidatos = [
        ("PROXIMA_LLEGADA_ASCENSOR", estado_actual["PROXIMA_LLEGADA_ASCENSOR"]),
        ("PROXIMA_LLEGADA_PASAJERO", estado_actual["PROXIMA_LLEGADA_PASAJERO"]),
        ("FIN_DESCENSO", estado_actual["FIN_DESCENSO"]),
        ("FIN_ASCENSO", estado_actual["FIN_ASCENSO"]),
        ("FIN_ESPERA", estado_actual["FIN_ESPERA"]),
    ]

    # Solo los que tienen tiempo cargado
    candidatos = [(nombre, tiempo) for nombre, tiempo in candidatos if tiempo is not None]

    # El de menor tiempo: (nombre, reloj)
    nombre_evento, reloj = min(candidatos, key=lambda item: item[1])
    return nombre_evento, reloj


def armar_estado_inicial(parametros):
    """
    Dos modos:
      - Con condiciones iniciales (H no es None): como el enunciado / Tp.ods.
      - Sin condiciones (H is None): arranque de cero; colas también None;
        se programan llegada de ascensor Y de pasajero.
    """
    h = parametros["H"]
    aleatorios = campos_aleatorios_vacios()

    rnd_l, llegada_pasajero = exponencial(parametros["media_llegada_pasajero"])
    aleatorios["RND_LLEGADA_PASAJERO"] = rnd_l
    aleatorios["LLEGADA_PASAJERO"] = llegada_pasajero
    proxima_llegada_pasajero = truncar(0.0 + llegada_pasajero, 2)

    # --- Arranque de cero (sin condiciones iniciales) ---
    if h is None:
        rnd_viaje, llegada_ascensor = uniforme(
            parametros["viaje_min"],
            parametros["viaje_max"],
        )
        aleatorios["RND_LLEGADA_ASCENSOR"] = rnd_viaje
        aleatorios["LLEGADA_ASCENSOR"] = llegada_ascensor
        return {
            "EVENTO": "inicializacion",
            "RELOJ": 0.0,
            **aleatorios,
            "H": None,
            "P": None,
            "PROXIMA_LLEGADA_ASCENSOR": truncar(0.0 + llegada_ascensor, 2),
            "PROXIMA_LLEGADA_PASAJERO": proxima_llegada_pasajero,
            "DIRECCION_ASCENSOR": "sube",
            "ESTADO_ASCENSOR": "en_movimiento",
            "ESPACIO_DISPONIBLE": parametros["capacidad"],
            "FIN_DESCENSO": None,
            "FIN_ASCENSO": None,
            "FIN_ESPERA": None,
            "INICIO_DETENCION": None,
            "COLA_BAJA": 0,
            "COLA_SUBE": 0,
            "ACUMULADOR_PERMANENCIA": 0.0,
        }

    # --- Con condiciones iniciales (enunciado) ---
    # H viene de parámetros (no hay RND_H). P se sortea.
    rnd_p, p = (None, None)
    if h > 0:
        rnd_p, p = uniforme_entero(0, h)
    aleatorios["RND_P"] = rnd_p

    cola_baja = parametros["cola_bajan"]
    cola_sube = parametros["cola_suben"]
    direccion_ascensor = parametros["direccion_ascensor"]

    fin_descenso = None
    fin_ascenso = None
    fin_espera = None
    estado_ascensor = None
    h_actual = h
    espacio = parametros["capacidad"] - h
    proxima_llegada_ascensor = None
    llegada_ascensor = None
    inicio_detencion = 0.0

    if p is not None and p > 0:
        fin_descenso = truncar(0.0 + p * parametros["tiempo_descenso_d"], 2)
        estado_ascensor = "esperando_descenso"
    else:
        if p is None:
            espacio = parametros["capacidad"] - h
        else:
            espacio = parametros["capacidad"] - (h - p)
        cola_dir = cola_sube if direccion_ascensor == "sube" else cola_baja

        if cola_dir > 0 and espacio > 0:
            cuantos_suben = min(cola_dir, espacio)
            fin_ascenso = truncar(0.0 + cuantos_suben * parametros["tiempo_ascenso_a"], 2)
            estado_ascensor = "esperando_ascenso"

            if direccion_ascensor == "sube":
                cola_sube -= cuantos_suben
            else:
                cola_baja -= cuantos_suben
                
            espacio -= cuantos_suben
        else:
            inicio_detencion = None
            estado_ascensor = "en_movimiento"
            rnd_viaje, llegada_ascensor = uniforme(
                parametros["viaje_min"],
                parametros["viaje_max"],
            )
            aleatorios["RND_LLEGADA_ASCENSOR"] = rnd_viaje
            aleatorios["LLEGADA_ASCENSOR"] = llegada_ascensor
            proxima_llegada_ascensor = truncar(0.0 + llegada_ascensor, 2)

    return {
        "EVENTO": "inicializacion",
        "RELOJ": 0.0,
        **aleatorios,
        "H": h_actual,
        "P": p,
        "PROXIMA_LLEGADA_ASCENSOR": proxima_llegada_ascensor,
        "PROXIMA_LLEGADA_PASAJERO": proxima_llegada_pasajero,
        "DIRECCION_ASCENSOR": direccion_ascensor,
        "ESTADO_ASCENSOR": estado_ascensor,
        "ESPACIO_DISPONIBLE": espacio,
        "FIN_DESCENSO": fin_descenso,
        "FIN_ASCENSO": fin_ascenso,
        "FIN_ESPERA": fin_espera,
        "INICIO_DETENCION": inicio_detencion,
        "COLA_BAJA": cola_baja,
        "COLA_SUBE": cola_sube,
        "ACUMULADOR_PERMANENCIA": 0.0,
    }

def armar_estado_actual(estado_anterior, parametros):
    """
    Arma el estado actual basado en el estado anterior.
    """
    proximo_evento, reloj = determinar_proximo_evento(estado_anterior)
    if proximo_evento == "PROXIMA_LLEGADA_ASCENSOR":
        estado_actual = simular_llegada_ascensor(estado_anterior, parametros, reloj)
    elif proximo_evento == "PROXIMA_LLEGADA_PASAJERO":
        estado_actual = simular_llegada_pasajero(estado_anterior, parametros, reloj)
    elif proximo_evento == "FIN_DESCENSO":
        estado_actual = simular_fin_descenso(estado_anterior, parametros, reloj)
    elif proximo_evento == "FIN_ASCENSO":
        estado_actual = simular_fin_ascenso(estado_anterior, parametros, reloj)
    elif proximo_evento == "FIN_ESPERA":
        estado_actual = simular_fin_espera(estado_anterior, parametros, reloj)
    return estado_actual