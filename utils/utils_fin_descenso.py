def simular_fin_descenso(estado_anterior, parametros, reloj):
    """
    Simula el fin de descenso de un ascensor.
    """
    evento = "fin_descenso"
    reloj = estado_anterior["FIN_DESCENSO"]
    h = estado_anterior["H"]
    # Si H = 0 no hay nadie a bordo → P no se calcula, es None
    p = estado_anterior["P"] 
    direccion_ascensor = estado_anterior["DIRECCION_ASCENSOR"]
    estado_ascensor = definir_estado(estado_anterior["P"], estado_anterior["ESPACIO_DISPONIBLE"], estado_anterior["COLA_BAJA"], estado_anterior["COLA_SUBE"], estado_anterior["DIRECCION_ASCENSOR"])
    proxima_llegada_ascensor = estado_anterior["PROXIMA_LLEGADA_ASCENSOR"]
    proxima_llegada_pasajero = estado_anterior["PROXIMA_LLEGADA_PASAJERO"]
    espacio_disponible = parametros["capacidad"] - (h - p) if p is not None else parametros["capacidad"]
    fin_descenso = None
    fin_ascenso = reloj + parametros["tiempo_ascenso_a"] * calcular_numero_de_ascensos(estado_anterior["COLA_BAJA"], estado_anterior["COLA_SUBE"], espacio_disponible, estado_anterior["DIRECCION_ASCENSOR"]) if estado_ascensor == "esperando_ascenso"  and p is not None else None
    fin_espera = calcular_fin_espera(p,reloj, estado_anterior["COLA_BAJA"], estado_anterior["COLA_SUBE"], estado_anterior["ESPACIO_DISPONIBLE"], estado_anterior["DIRECCION_ASCENSOR"], parametros)
    inicio_detencion = estado_anterior["INICIO_DETENCION"]
    cola_baja = estado_anterior["COLA_BAJA"]
    cola_sube = estado_anterior["COLA_SUBE"]
    acumulador_permanencia = estado_anterior["ACUMULADOR_PERMANENCIA"]

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

def calcular_numero_de_ascensos(cola_baja, cola_sube, espacio_disponible, direccion_ascensor):
    if espacio_disponible == 0:
        return 0
    elif direccion_ascensor == "sube":
        return min(cola_sube, espacio_disponible)
    return min(cola_baja, espacio_disponible)

def calcular_fin_espera(p, reloj, cola_baja, cola_sube, espacio_disponible, direccion_ascensor, parametros):
    nro_ascensos = calcular_numero_de_ascensos(cola_baja, cola_sube, espacio_disponible, direccion_ascensor)
    if nro_ascensos > 0:
        return None
    return reloj + parametros["tiempo_espera_e"]

def definir_estado(p, espacio_disponible, cola_baja, cola_sube, direccion_ascensor):
    nro_ascensos = calcular_numero_de_ascensos(cola_baja, cola_sube, espacio_disponible, direccion_ascensor)
    if nro_ascensos > 0:
        return "esperando_ascenso"
    return "esperando"

