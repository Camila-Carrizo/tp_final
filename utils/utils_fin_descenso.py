from distribuciones import truncar, campos_aleatorios_vacios


def simular_fin_descenso(estado_anterior, parametros, reloj):
    """
    Simula el fin de descenso de un ascensor.
    Espacio post-descenso = capacidad - (H - P); si abordan, también se resta de la cola y del espacio.
    """
    evento = "fin_descenso"
    reloj = estado_anterior["FIN_DESCENSO"]
    h = estado_anterior["H"]
    p = estado_anterior["P"]
    direccion_ascensor = estado_anterior["DIRECCION_ASCENSOR"]
    cola_baja_ant = estado_anterior["COLA_BAJA"]
    cola_sube_ant = estado_anterior["COLA_SUBE"]

    espacio_disponible = (
        parametros["capacidad"] - (h - p) if p is not None else parametros["capacidad"]
    )

    estado_ascensor = definir_estado(
        espacio_disponible,
        cola_baja_ant,
        cola_sube_ant,
        direccion_ascensor,
    )

    proxima_llegada_ascensor = estado_anterior["PROXIMA_LLEGADA_ASCENSOR"]
    proxima_llegada_pasajero = estado_anterior["PROXIMA_LLEGADA_PASAJERO"]
    fin_descenso = None
    cuantos_suben = (
        calcular_numero_de_ascensos(
            cola_baja_ant,
            cola_sube_ant,
            espacio_disponible,
            direccion_ascensor,
        )
        if estado_ascensor == "esperando_ascenso"
        else 0
    )

    fin_ascenso = (
        truncar(reloj + parametros["tiempo_ascenso_a"] * cuantos_suben, 2)
        if estado_ascensor == "esperando_ascenso" and cuantos_suben > 0
        else None
    )
    fin_espera = calcular_fin_espera(
        reloj,
        cola_baja_ant,
        cola_sube_ant,
        espacio_disponible,
        direccion_ascensor,
        parametros,
    )

    inicio_detencion = estado_anterior["INICIO_DETENCION"]
    cola_baja = (
        calcular_colas(
            cola_baja_ant,
            cola_sube_ant,
            espacio_disponible,
            direccion_ascensor,
        )
        if (direccion_ascensor == "baja" and estado_ascensor == "esperando_ascenso")
        else cola_baja_ant
    )
    cola_sube = (
        calcular_colas(
            cola_baja_ant,
            cola_sube_ant,
            espacio_disponible,
            direccion_ascensor,
        )
        if (direccion_ascensor == "sube" and estado_ascensor == "esperando_ascenso")
        else cola_sube_ant
    )
    if cuantos_suben > 0:
        espacio_disponible -= cuantos_suben
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


def calcular_numero_de_ascensos(cola_baja, cola_sube, espacio_disponible, direccion_ascensor):
    if espacio_disponible == 0:
        return 0
    elif direccion_ascensor == "sube":
        return min(cola_sube, espacio_disponible)
    return min(cola_baja, espacio_disponible)


def calcular_fin_espera(reloj, cola_baja, cola_sube, espacio_disponible, direccion_ascensor, parametros):
    nro_ascensos = calcular_numero_de_ascensos(cola_baja, cola_sube, espacio_disponible, direccion_ascensor)
    if nro_ascensos > 0:
        return None
    return truncar(reloj + parametros["tiempo_espera_e"], 2)


def definir_estado(espacio_disponible, cola_baja, cola_sube, direccion_ascensor):
    nro_ascensos = calcular_numero_de_ascensos(cola_baja, cola_sube, espacio_disponible, direccion_ascensor)
    if nro_ascensos > 0:
        return "esperando_ascenso"
    return "esperando"


def calcular_colas(cola_baja, cola_sube, espacio_disponible, direccion_ascensor):
    nro_ascensos = calcular_numero_de_ascensos(cola_baja, cola_sube, espacio_disponible, direccion_ascensor)
    cola_dir = cola_baja if direccion_ascensor == "baja" else cola_sube
    cola_dir = cola_dir - nro_ascensos
    return cola_dir
