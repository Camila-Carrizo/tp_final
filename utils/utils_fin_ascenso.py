from distribuciones import truncar, campos_aleatorios_vacios


def simular_fin_ascenso(estado_anterior, parametros, reloj):
    """
    Simula el fin de ascenso de un ascensor.
    """
    evento = "fin_ascenso"
    reloj = estado_anterior["FIN_ASCENSO"]
    h = estado_anterior["H"]
    p = estado_anterior["P"]
    direccion_ascensor = estado_anterior["DIRECCION_ASCENSOR"]
    estado_ascensor = "esperando"
    proxima_llegada_ascensor = estado_anterior["PROXIMA_LLEGADA_ASCENSOR"]
    proxima_llegada_pasajero = estado_anterior["PROXIMA_LLEGADA_PASAJERO"]
    espacio_disponible = (
        parametros["capacidad"] - (h - p) if p is not None else parametros["capacidad"]
    )
    fin_descenso = None
    fin_ascenso = None
    fin_espera = truncar(reloj + parametros["tiempo_espera_e"], 2)
    inicio_detencion = estado_anterior["INICIO_DETENCION"]
    cola_baja = estado_anterior["COLA_BAJA"]
    cola_sube = estado_anterior["COLA_SUBE"]
    acumulador_permanencia = estado_anterior["ACUMULADOR_PERMANENCIA"]

    return {
        "EVENTO": evento,
        "RELOJ": reloj,
        **campos_aleatorios_vacios(),
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
