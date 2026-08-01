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
    espacio_disponible = parametros["capacidad"]
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



