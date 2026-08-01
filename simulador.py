"""
simulador.py
------------
Acá se va a hacer la simulación.

Solo guardamos 2 filas (como en el Excel):
  - estado_anterior: la de arriba
  - estado_actual: la que estamos armando
"""

import random

from parametros import crear_parametros
from distribuciones import uniforme, uniforme_entero, exponencial
from utils.utils_llegada_ascensor import simular_llegada_ascensor
from utils.utils_llegada_pasajeros import simular_llegada_pasajero
from utils.utils_fin_descenso import simular_fin_descenso
from utils.utils_fin_ascenso import simular_fin_ascenso
from utils.utils_fin_espera import simular_fin_espera


def ejecutar():
    # 1) Parámetros de inicio (números del enunciado)
    parametros = crear_parametros()

    if parametros["semilla"] is not None:
        random.seed(parametros["semilla"])

    # 2) Fila inicial
    estado_anterior = {}
    estado_actual = armar_estado_inicial(parametros)
    cantidad_eventos = parametros["cantidad_eventos"]

    for i in range(cantidad_eventos):
        if i == 0:
            estado_actual = armar_estado_inicial(parametros)
        else:
            estado_anterior = estado_actual
            estado_actual = armar_estado_actual(estado_anterior, parametros)
            
    return estado_actual

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
    proxima_llegada_pasajero = exponencial(parametros["media_llegada_pasajero"])

    # --- Arranque de cero (sin condiciones iniciales) ---
    if h is None:
        proxima_llegada_ascensor = uniforme(
            parametros["viaje_min"],
            parametros["viaje_max"],
        )
        return {
            "EVENTO": "inicializacion",
            "RELOJ": 0.0,
            "H": None,
            "P": None,
            "PROXIMA_LLEGADA_ASCENSOR": 0.0 + proxima_llegada_ascensor,
            "PROXIMA_LLEGADA_PASAJERO": 0.0 + proxima_llegada_pasajero,
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
    # En t=0 el ascensor ya está en el piso 15, con H pasajeros.
    # P siempre se calcula acá (no viene de parámetros / UI).
    p = uniforme_entero(0, h) if h > 0 else None
    cola_baja = parametros["cola_bajan"]
    cola_sube = parametros["cola_suben"]
    direccion_ascensor = parametros["direccion_ascensor"]

    fin_descenso = None
    fin_ascenso = None
    fin_espera = None
    estado_ascensor = None
    h_actual = h
    # Mientras aún no bajaron: ocupados = H
    espacio = parametros["capacidad"] - h
    proxima_llegada_ascensor = None
    inicio_detencion = 0.0  # se detiene (salvo el caso "no para" de abajo)

    if p is not None and p > 0:
        # Hay descenso: primero se programa Fin Descenso.
        # El ascenso se verá en ese evento (después).
        fin_descenso = 0.0 + p * parametros["tiempo_descenso_d"]
        estado_ascensor = "esperando_descenso"
    else:
        # P = 0 o None → no hay descenso: se sigue directo con ascenso,
        # solo si hay cola en la dirección del ascensor y espacio > 0.
        # Espacio disponible = capacidad - (H - P)  (con P=0 → capacidad - H)
        if p is None:
            espacio = parametros["capacidad"] - h
        else:   
            espacio = parametros["capacidad"] - (h - p)
        cola_dir = cola_sube if direccion_ascensor == "sube" else cola_baja

        if cola_dir > 0 and espacio > 0:
            cuantos_suben = min(cola_dir, espacio)
            fin_ascenso = 0.0 + cuantos_suben * parametros["tiempo_ascenso_a"]
            estado_ascensor = "esperando_ascenso"

            # Salen de la cola al abordar (como en el Tp.ods)
            if direccion_ascensor == "sube":
                cola_sube -= cuantos_suben
            else:
                cola_baja -= cuantos_suben

            h_actual = h + cuantos_suben  # P=0, nadie bajó
            espacio = parametros["capacidad"] - h_actual
        else:
            # Nadie desciende y nadie asciende → NO se detiene.
            # Efecto de "fin espera" sin esperar E ni acumular detención:
            # se programa la próxima llegada del ascensor.
            inicio_detencion = None
            estado_ascensor = "en_movimiento"
            proxima_llegada_ascensor = 0.0 + uniforme(
                parametros["viaje_min"],
                parametros["viaje_max"],
            )

    return {
        "EVENTO": "inicializacion",
        "RELOJ": 0.0,
        "H": h_actual,
        "P": p,
        "PROXIMA_LLEGADA_ASCENSOR": proxima_llegada_ascensor,
        "PROXIMA_LLEGADA_PASAJERO": 0.0 + proxima_llegada_pasajero,
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