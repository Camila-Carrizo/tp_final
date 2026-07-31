# Evento Llegada Ascensor 

1. Obtener H.
2. Obtener P.
3. Calcular ocupación del ascensor.
4. Verificar si el ascensor se detiene.
5. Si se detiene:
    - Programar el siguiente evento.
    - Guardar tiempo de detención
6. Si no se detiene:
    - Programar la próxima llegada del ascensor.

# Evento Llegada Pasajero
1. Generar dirección del pasajero.
2. Verificar si puede subir inmediatamente al ascensor.
3. Si puede subir:
    - Recalcular el evento Fin Ascenso 
4. Si no puede subir:
    - Agregar el pasajero a la cola correspondiente.
5. Programar la próxima llegada de pasajero.

# Evento Fin Descenso
1. Recalcular el espacio disponible
2. Si hay pasajeros que puedan ascender:
    -Recalcular Colas
    -Programar ascenso
3- Si no hay pasajeros que puedan descender:
    -Programar espera

# Evento Fin Ascenso
1. Recalcular el espacio disponible
2. Programar espera

# Envento Fin Espera
1. Programar la proxima llegada del ascensor
2. Acumular tiempo de detencion

