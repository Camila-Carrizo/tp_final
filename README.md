# Simulación del ascensor (Ejercicio 124) — estilo funcional

## Idea

No hay clase `Simulador`. Hay **funciones** y un diccionario **`estado`**.

```
main.py
  → parametros = crear_parametros()
  → estado = inicializar(parametros)
  → resultado = ejecutar(estado, parametros)

ejecutar(...)
  → (después) mientras haya eventos:
       saca el próximo
       si "llegada_ascensor" → llegada_ascensor(estado, parametros)
       si "llegada_pasajero" → llegada_pasajero(estado, parametros)
       ...
```

## Archivos

| Archivo | Qué hace |
|---------|----------|
| `main.py` | Arma todo y muestra el resultado |
| `simulador.py` | `inicializar`, `ejecutar` y funciones por evento |
| `distribuciones.py` | Randoms |
| `parametros.py` | `crear_parametros()` → dict |
| `ui.py` | Tkinter (después) |
| `excel.py` | Excel (después) |

## Cómo correr

```bash
cd simulacion_ascensor
python main.py
```

## Estado actual

- Distribuciones listas
- `ejecutar` es esqueleto (sin loop todavía)
- UI y Excel vacíos a propósito
