from distribuciones import uniforme_entero, uniforme, truncar, campos_aleatorios_vacios


def simular_llegada_ascensor(estado_anterior, parametros, reloj):
    """
    Simula la llegada de un ascensor.
    Sorteos de este evento: RND_H/H, RND_P/P, y si no para: RND viaje.
    """
    evento = "llegada_ascensor"
    reloj = estado_anterior["PROXIMA_LLEGADA_ASCENSOR"]
    aleatorios = campos_aleatorios_vacios()

    rnd_h, h = uniforme_entero(0, parametros["capacidad"])
    aleatorios["RND_H"] = rnd_h

    rnd_p, p = (None, None)
    if h > 0:
        rnd_p, p = uniforme_entero(0, h)
    aleatorios["RND_P"] = rnd_p

    direccion_ascensor = estado_anterior["DIRECCION_ASCENSOR"]
    proxima_llegada_pasajero = estado_anterior["PROXIMA_LLEGADA_PASAJERO"]
    espacio_disponible = parametros["capacidad"] - h
    estado_ascensor = definir_estado(
        p,
        espacio_disponible,
        estado_anterior["COLA_BAJA"],
        estado_anterior["COLA_SUBE"],
        estado_anterior["DIRECCION_ASCENSOR"],
    )

    if estado_ascensor == "en_movimiento":
        rnd_viaje, llegada_ascensor = uniforme(
            parametros["viaje_min"],
            parametros["viaje_max"],
        )
        aleatorios["RND_LLEGADA_ASCENSOR"] = rnd_viaje
        aleatorios["LLEGADA_ASCENSOR"] = llegada_ascensor
        proxima_llegada_ascensor = truncar(reloj + llegada_ascensor, 2)
    else:
        proxima_llegada_ascensor = estado_anterior["PROXIMA_LLEGADA_ASCENSOR"]

    fin_descenso = (
        truncar(reloj + p * parametros["tiempo_descenso_d"], 2)
        if estado_ascensor == "esperando_descenso" and p is not None
        else None
    )
    fin_espera = None
    inicio_detencion = reloj if estado_ascensor != "en_movimiento" else None
    cola_baja, cola_sube, cuantos_suben = calcular_cola(
        estado_ascensor,
        estado_anterior["DIRECCION_ASCENSOR"],
        espacio_disponible,
        estado_anterior["COLA_BAJA"],
        estado_anterior["COLA_SUBE"],
    )
    if cuantos_suben > 0:
        espacio_disponible -= cuantos_suben
    fin_ascenso = (
        truncar(reloj + parametros["tiempo_ascenso_a"] * cuantos_suben, 2)
        if estado_ascensor == "esperando_ascenso" and cuantos_suben > 0
        else None
    )
    if estado_ascensor == "en_movimiento":
        acumulador_permanencia = truncar(
            estado_anterior["ACUMULADOR_PERMANENCIA"] + reloj - estado_anterior["RELOJ"],
            2,
        )
    else:
        acumulador_permanencia = estado_anterior["ACUMULADOR_PERMANENCIA"]

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


def calcular_cola(estado_ascensor, direccion_ascensor, espacio_disponible, cola_baja, cola_sube):
    cuantos_suben = 0
    if estado_ascensor != "esperando_ascenso":
        return cola_baja, cola_sube, cuantos_suben

    if direccion_ascensor == "sube":
        cuantos_suben = min(cola_sube, espacio_disponible)
        return cola_baja, cola_sube - cuantos_suben, cuantos_suben

    cuantos_suben = min(cola_baja, espacio_disponible)
    return cola_baja - cuantos_suben, cola_sube, cuantos_suben


def definir_estado(p, espacio_disponible, cola_baja, cola_sube, direccion_ascensor):
    if p is not None and p > 0:
        return "esperando_descenso"

    cola_dir = cola_sube if direccion_ascensor == "sube" else cola_baja
    if cola_dir > 0 and espacio_disponible > 0:
        return "esperando_ascenso"

    return "en_movimiento"
