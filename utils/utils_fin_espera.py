from distribuciones import uniforme_entero, exponencial, uniforme


def simular_fin_espera(estado_anterior, parametros, reloj):
    """
    Simula el fin de espera de un ascensor.
    """
    evento = "fin_espera"
    reloj = estado_anterior["FIN_ESPERA"]
    h = estado_anterior["H"]
    # Si H = 0 no hay nadie a bordo → P no se calcula
    p = estado_anterior["P"]
    direccion_ascensor = "sube" if estado_anterior["DIRECCION_ASCENSOR"] == "baja" else "baja"
    estado_ascensor = "en_movimiento"
    proxima_llegada_ascensor = reloj + uniforme(parametros["viaje_min"], parametros["viaje_max"])
    proxima_llegada_pasajero = estado_anterior["PROXIMA_LLEGADA_PASAJERO"]
    espacio_disponible = 6
    fin_descenso = None
    fin_ascenso = None
    fin_espera = None
    inicio_detencion = None
    cola_baja = estado_anterior["COLA_BAJA"]
    cola_sube = estado_anterior["COLA_SUBE"]
    acumulador_permanencia = estado_anterior["ACUMULADOR_PERMANENCIA"] + reloj - estado_anterior["INICIO_DETENCION"]

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

def calcular_numero_de_ascensos(p,cola_baja, cola_sube, espacio_disponible, direccion_ascensor):
    if p is None or p == 0 or espacio_disponible == 0:
        return None
    elif direccion_ascensor == "sube":
        return min(cola_sube, espacio_disponible)
    return min(cola_baja, espacio_disponible)

def calcular_fin_espera(p, reloj, cola_baja, cola_sube, espacio_disponible, direccion_ascensor):
    nro_ascensos = calcular_numero_de_ascensos(cola_baja, cola_sube, espacio_disponible, direccion_ascensor)
    if nro_ascensos is None:
        return None
    return reloj + 5

def definir_estado(espacio_disponible, cola_baja, cola_sube, direccion_ascensor):
    nro_ascensos = calcular_numero_de_ascensos(cola_baja, cola_sube, espacio_disponible, direccion_ascensor)
    if nro_ascensos is not None:
        return "esperando_ascenso"
    return "esperando"

