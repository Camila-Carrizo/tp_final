from calendar import c
from distribuciones import uniforme_entero, exponencial, uniforme


def simular_llegada_pasajero(estado_anterior, parametros, reloj):
    
    """
    Simula la llegada de un pasajero.
    """
    evento = "llegada_pasajero"
    reloj = estado_anterior["PROXIMA_LLEGADA_PASAJERO"]
    h = estado_anterior["H"]
    p = estado_anterior["P"]
    direccion_ascensor = estado_anterior["DIRECCION_ASCENSOR"]
    proxima_llegada_ascensor = estado_anterior["PROXIMA_LLEGADA_ASCENSOR"]
    proxima_llegada_pasajero = reloj + exponencial(parametros["media_llegada_pasajero"])
    espacio_disponible = estado_anterior["ESPACIO_DISPONIBLE"] -1 if accedio_al_ascensor(estado_anterior["DIRECCION_ASCENSOR"], estado_anterior["ESPACIO_DISPONIBLE"])[1] else estado_anterior["ESPACIO_DISPONIBLE"]
    fin_descenso = estado_anterior["FIN_DESCENSO"]
    inicio_detencion = estado_anterior["INICIO_DETENCION"]
    acumulador_permanencia = estado_anterior["ACUMULADOR_PERMANENCIA"]
    cola_baja, cola_sube, fin_espera, fin_ascenso, estado_ascensor = calcular_cola_tiempos_estados(estado_anterior["ESPACIO_DISPONIBLE"], estado_anterior["COLA_BAJA"], estado_anterior["COLA_SUBE"], estado_anterior["FIN_ASCENSO"], estado_anterior["FIN_ESPERA"], estado_ascensor, reloj, parametros, estado_anterior["DIRECCION_ASCENSOR"])

    return {
        "EVENTO": evento,
        "RELOJ": reloj,
        "H": h,
        "P": p,
        "PROXIMA_LLEGADA_ASCENSOR": proxima_llegada_ascensor,
        "PROXIMA_LLEGADA_PASAJERO": proxima_llegada_pasajero,
        "DIRECCION_ASCENSOR": direccion_ascensor,
        "ESTADO_ASCENSOR": estado_ascensor,
        "ESPACIO_DISPONIBLE":  espacio_disponible,
        "FIN_DESCENSO": fin_descenso,
        "FIN_ASCENSO": fin_ascenso,
        "FIN_ESPERA": fin_espera,
        "INICIO_DETENCION": inicio_detencion,
        "COLA_BAJA": cola_baja,
        "COLA_SUBE": cola_sube,
        "ACUMULADOR_PERMANENCIA": acumulador_permanencia,
    }

def calcular_cola_tiempos_estados(espacio_disponible, cola_baja, cola_sube, fin_ascenso, fin_espera, estado_ascensor, reloj, parametros, direccion_ascensor):
    """
    Determina si el pasajero accede al ascensor.
    """
    direccion_pasajero, accedio_al_ascensor = accedio_al_ascensor(direccion_ascensor, espacio_disponible)

    #No puede subir en el momento y va a cola de espera
    if not accedio_al_ascensor or estado_ascensor in ["en_movimiento", "esperando_descenso"]:
        if direccion_pasajero == "baja":
            cola_baja = cola_baja + 1
        else:
            cola_sube = cola_sube + 1

    #recalculo de tiempos cuando SI PUEDE subir en el momento
    if estado_ascensor == "esperando" and accedio_al_ascensor:
        fin_espera = reloj + parametros["tiempo_espera_e"]
        estado_ascensor = "esperando_ascenso"
    elif estado_ascensor == "esperando_ascenso" and accedio_al_ascensor:
        fin_ascenso = reloj + (fin_ascenso - reloj) + parametros["tiempo_espera_a"]	

    return cola_baja, cola_sube, fin_espera, fin_ascenso, estado_ascensor

def accedio_al_ascensor(direccion_ascensor, espacio_disponible):
    direccion_pasajero = direccion_pasajero()
    if (direccion_pasajero != direccion_ascensor) or (direccion_pasajero == direccion_ascensor and espacio_disponible <= 0):
        return direccion_pasajero, False
    if direccion_pasajero == direccion_ascensor and espacio_disponible > 0:
        return direccion_pasajero, True


