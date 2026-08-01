from distribuciones import uniforme_entero, exponencial, uniforme


def simular_llegada_ascensor(estado_anterior, parametros, reloj):
    """
    Simula la llegada de un ascensor.
    """
    evento = "llegada_ascensor"
    reloj = estado_anterior["PROXIMA_LLEGADA_ASCENSOR"]
    h = uniforme_entero(0, parametros["capacidad"])
    # Si H = 0 no hay nadie a bordo → P no se calcula
    p = uniforme_entero(0, h) if h > 0 else None
    direccion_ascensor = estado_anterior["DIRECCION_ASCENSOR"]
    proxima_llegada_pasajero = estado_anterior["PROXIMA_LLEGADA_PASAJERO"]
    espacio_disponible = parametros["capacidad"] - h
    estado_ascensor = definir_estado(p, espacio_disponible, estado_anterior["COLA_BAJA"], estado_anterior["COLA_SUBE"], estado_anterior["DIRECCION_ASCENSOR"])
    proxima_llegada_ascensor = reloj + uniforme(parametros["viaje_min"], parametros["viaje_max"]) if estado_ascensor == "en_movimiento" else estado_anterior["PROXIMA_LLEGADA_ASCENSOR"]
    fin_descenso = reloj + p * parametros["tiempo_descenso_d"] if estado_ascensor == "esperando_descenso" and p is not None else None
    fin_espera = None
    inicio_detencion = reloj if estado_ascensor != "en_movimiento" else None
    cola_baja, cola_sube, cuantos_suben = calcular_cola(
        estado_ascensor,
        estado_anterior["DIRECCION_ASCENSOR"],
        espacio_disponible,
        estado_anterior["COLA_BAJA"],
        estado_anterior["COLA_SUBE"],
    )
    fin_ascenso = reloj + parametros["tiempo_ascenso_a"] * cuantos_suben if estado_ascensor == "esperando_ascenso" and p is not None else None
    acumulador_permanencia = estado_anterior["ACUMULADOR_PERMANENCIA"] + reloj - estado_anterior["RELOJ"] if estado_ascensor == "en_movimiento" else estado_anterior["ACUMULADOR_PERMANENCIA"]

    return {
        "EVENTO": evento,
        "RELOJ": reloj,
        "H": h,
        "P": p,
        "PROXIMA_LLEGADA_ASCENSOR": proxima_llegada_ascensor,
        "PROXIMA_LLEGADA_PASAJERO": proxima_llegada_pasajero,
        "DIRECCION_ASCENSOR": direccion_ascensor,
        "ESTADO_ASCENSOR": estado_ascensor,
        "ESPACIO_DISPONIBLE": espacio_disponible,
        "FIN_DESCENSO": fin_descenso,
        "FIN_ASCENSO": fin_ascenso,
        "FIN_ESPERA": fin_espera,
        "INICIO_DETENCION": inicio_detencion,
        "COLA_BAJA": cola_baja,
        "COLA_SUBE": cola_sube,
        "ACUMULADOR_PERMANENCIA": acumulador_permanencia,
    }

def calcular_cola(estado_ascensor, direccion_ascensor, espacio_disponible, cola_baja, cola_sube):
    cuantos_suben = 0
    """
    Si el estado_ascensor es esperando_ascenso, bajan de la cola de esa dirección
    la cantidad que realmente puede subir: min(cola, espacio_disponible).
    Si no, las colas quedan igual.
    Devuelve: (cola_baja, cola_sube)
    """
    if estado_ascensor != "esperando_ascenso":
        return cola_baja, cola_sube, cuantos_suben

    if direccion_ascensor == "sube":
        cuantos_suben = min(cola_sube, espacio_disponible)
        return cola_baja, cola_sube - cuantos_suben, cuantos_suben

    cuantos_suben = min(cola_baja, espacio_disponible)
    return cola_baja - cuantos_suben, cola_sube, cuantos_suben


def definir_estado(p, espacio_disponible, cola_baja, cola_sube, direccion_ascensor):
    """
    - Si P > 0 → alguien desciende → esperando_descenso
    - Si P es None (H=0) o P = 0 → nadie desciende; ¿hay quien ascienda?
        sí → esperando_ascenso
        no → en_movimiento (el ascensor no para)
    """
    if p is not None and p > 0:
        return "esperando_descenso"

    cola_dir = cola_sube if direccion_ascensor == "sube" else cola_baja
    if cola_dir > 0 and espacio_disponible > 0:
        return "esperando_ascenso"

    return "en_movimiento"

