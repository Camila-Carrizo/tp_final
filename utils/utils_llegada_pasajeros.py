from distribuciones import exponencial, definir_direccion_pasajero, truncar, campos_aleatorios_vacios


def simular_llegada_pasajero(estado_anterior, parametros, reloj):
    """
    Simula la llegada de un pasajero.
    Columnas aleatorias de este evento:
      RND_LLEGADA_PASAJERO → LLEGADA_PASAJERO → PROXIMA_LLEGADA_PASAJERO
      RND_DIRECCION_PASAJERO → DIRECCION_PASAJERO
    """
    evento = "llegada_pasajero"
    reloj = estado_anterior["PROXIMA_LLEGADA_PASAJERO"]
    h = estado_anterior["H"]
    p = estado_anterior["P"]
    direccion_ascensor = estado_anterior["DIRECCION_ASCENSOR"]
    proxima_llegada_ascensor = estado_anterior["PROXIMA_LLEGADA_ASCENSOR"]

    aleatorios = campos_aleatorios_vacios()
    rnd_l, llegada_pasajero = exponencial(parametros["media_llegada_pasajero"])
    aleatorios["RND_LLEGADA_PASAJERO"] = rnd_l
    aleatorios["LLEGADA_PASAJERO"] = llegada_pasajero
    proxima_llegada_pasajero = truncar(reloj + llegada_pasajero, 2)

    fin_descenso = estado_anterior["FIN_DESCENSO"]
    inicio_detencion = estado_anterior["INICIO_DETENCION"]
    acumulador_permanencia = estado_anterior["ACUMULADOR_PERMANENCIA"]

    (
        cola_baja,
        cola_sube,
        fin_espera,
        fin_ascenso,
        estado_ascensor,
        accede,
        rnd_dir,
        direccion_pasajero,
    ) = calcular_cola_tiempos_estados(
        estado_anterior["ESPACIO_DISPONIBLE"],
        estado_anterior["COLA_BAJA"],
        estado_anterior["COLA_SUBE"],
        estado_anterior["FIN_ASCENSO"],
        estado_anterior["FIN_ESPERA"],
        estado_anterior["ESTADO_ASCENSOR"],
        reloj,
        parametros,
        estado_anterior["DIRECCION_ASCENSOR"],
    )
    aleatorios["RND_DIRECCION_PASAJERO"] = rnd_dir
    aleatorios["DIRECCION_PASAJERO"] = direccion_pasajero

    espacio_disponible = (
        estado_anterior["ESPACIO_DISPONIBLE"] - 1
        if accede
        else estado_anterior["ESPACIO_DISPONIBLE"]
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


def calcular_cola_tiempos_estados(
    espacio_disponible,
    cola_baja,
    cola_sube,
    fin_ascenso,
    fin_espera,
    estado_ascensor,
    reloj,
    parametros,
    direccion_ascensor,
):
    """Determina si el pasajero accede al ascensor."""
    rnd_dir, direccion_pasajero, accede = accedio_al_ascensor(
        direccion_ascensor,
        espacio_disponible,
        parametros.get("probabilidad_bajar", 0.7),
    )

    if not accede or estado_ascensor in ["en_movimiento", "esperando_descenso"]:
        if direccion_pasajero == "baja":
            cola_baja = cola_baja + 1
            accede = False
        else:
            cola_sube = cola_sube + 1
            accede = False

    if estado_ascensor == "esperando" and accede:
        fin_espera = None
        fin_ascenso = truncar(reloj + parametros["tiempo_ascenso_a"], 2)
        estado_ascensor = "esperando_ascenso"
    elif estado_ascensor == "esperando_ascenso" and accede:
        fin_ascenso = truncar(
            reloj + (fin_ascenso - reloj) + parametros["tiempo_ascenso_a"],
            2,
        )

    return (
        cola_baja,
        cola_sube,
        fin_espera,
        fin_ascenso,
        estado_ascensor,
        accede,
        rnd_dir,
        direccion_pasajero,
    )


def accedio_al_ascensor(direccion_ascensor, espacio_disponible, probabilidad_bajar=0.7):
    rnd_dir, direccion_pasajero = definir_direccion_pasajero(probabilidad_bajar)
    if (direccion_pasajero != direccion_ascensor) or (
        direccion_pasajero == direccion_ascensor and espacio_disponible <= 0
    ):
        return rnd_dir, direccion_pasajero, False
    if direccion_pasajero == direccion_ascensor and espacio_disponible > 0:
        return rnd_dir, direccion_pasajero, True
    return rnd_dir, direccion_pasajero, False
