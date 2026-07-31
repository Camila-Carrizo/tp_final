"""
parametros.py
-------------
Números del enunciado.

crear_parametros() devuelve un diccionario con todos los valores.
Más adelante la UI puede armar el mismo diccionario con lo que cargue el usuario.
"""


def crear_parametros(**overrides):
    """
    Parámetros por defecto del Ejercicio 124.
    Se pueden pisar valores: crear_parametros(capacidad=8, semilla=1)
    """
    p = {
        # Cantidad de eventos a simular
        "cantidad_eventos": 20,
        # Capacidad del ascensor
        "capacidad": 6,
        # Tiempos constantes (segundos)
        "tiempo_espera_e": 5.0,
        "tiempo_descenso_d": 5.0,
        "tiempo_ascenso_a": 5.0,
        # Llegada de pasajeros: Exp(media) en segundos
        "media_llegada_pasajero": 300.0,
        # 70% baja, 30% sube
        "probabilidad_bajar": 0.7,
        # Viaje entre pasadas: U(3;9) min → segundos
        "viaje_min": 180.0,
        "viaje_max": 540.0,
        # Hasta cuándo simular (0 = lo definimos después)
        "tiempo_fin": 0.0,
        # Condiciones iniciales del enunciado.
        # Si H es None → arranque "de cero" (sin condiciones iniciales):
        #   también cola_bajan y cola_suben deben ser None.
        # Si H tiene valor → se usan H y las colas como en el enunciado.
        # P NUNCA lo carga el usuario: siempre se calcula (U(0; H)).
        "H": 5,
        "direccion_ascensor": "sube", 
        "cola_bajan": 5,
        "cola_suben": 3,
        # Semilla opcional
        "semilla": None,
    }
    p.update(overrides)
    return p
