from distribuciones import uniforme, truncar, campos_aleatorios_vacios


def simular_fin_espera(estado_anterior, parametros, reloj):
    """
    Simula el fin de espera de un ascensor.
    Sorteo: RND_LLEGADA_ASCENSOR → LLEGADA_ASCENSOR → PROXIMA_LLEGADA_ASCENSOR
    """
    evento = "fin_espera"
    reloj = estado_anterior["FIN_ESPERA"]
    h = estado_anterior["H"]
    p = estado_anterior["P"]
    direccion_ascensor = (
        "sube" if estado_anterior["DIRECCION_ASCENSOR"] == "baja" else "baja"
    )
    estado_ascensor = "en_movimiento"

    aleatorios = campos_aleatorios_vacios()
    rnd_viaje, llegada_ascensor = uniforme(
        parametros["viaje_min"],
        parametros["viaje_max"],
    )
    aleatorios["RND_LLEGADA_ASCENSOR"] = rnd_viaje
    aleatorios["LLEGADA_ASCENSOR"] = llegada_ascensor
    proxima_llegada_ascensor = truncar(reloj + llegada_ascensor, 2)

    proxima_llegada_pasajero = estado_anterior["PROXIMA_LLEGADA_PASAJERO"]
    espacio_disponible = parametros["capacidad"]
    fin_descenso = None
    fin_ascenso = None
    fin_espera = None
    inicio_detencion = None
    cola_baja = estado_anterior["COLA_BAJA"]
    cola_sube = estado_anterior["COLA_SUBE"]
    acumulador_permanencia = truncar(
        estado_anterior["ACUMULADOR_PERMANENCIA"]
        + reloj
        - estado_anterior["INICIO_DETENCION"],
        2,
    )

    return {
        "EVENTO": evento,
        "RELOJ": reloj,
        **aleatorios,
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
