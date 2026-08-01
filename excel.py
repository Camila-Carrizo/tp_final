"""
excel.py
--------
Escribe cada fila de la simulación al .xlsx (sin acumular en memoria)
y permite leerlas después (p. ej. desde la UI).
"""

from __future__ import annotations

from pathlib import Path

from openpyxl import Workbook, load_workbook

# Orden: RND + valor crudo al lado de cada tiempo programado
COLUMNAS = [
    "EVENTO",
    "RELOJ",
    "RND_H",
    "H",
    "RND_P",
    "P",
    "RND_LLEGADA_PASAJERO",
    "LLEGADA_PASAJERO",
    "PROXIMA_LLEGADA_PASAJERO",
    "RND_LLEGADA_ASCENSOR",
    "LLEGADA_ASCENSOR",
    "PROXIMA_LLEGADA_ASCENSOR",
    "RND_DIRECCION_PASAJERO",
    "DIRECCION_PASAJERO",
    "DIRECCION_ASCENSOR",
    "ESTADO_ASCENSOR",
    "ESPACIO_DISPONIBLE",
    "FIN_DESCENSO",
    "FIN_ASCENSO",
    "FIN_ESPERA",
    "INICIO_DETENCION",
    "COLA_BAJA",
    "COLA_SUBE",
    "ACUMULADOR_PERMANENCIA",
]


class EscritorExcel:
    """Libro en disco: encabezado + append de filas + guardar al final."""

    def __init__(self, ruta_archivo: str | Path):
        self.ruta = Path(ruta_archivo)
        # Cada corrida arranca de cero: borra el Excel anterior si existe
        if self.ruta.exists():
            self.ruta.unlink()
        self.wb = Workbook()
        self.ws = self.wb.active
        self.ws.title = "Simulacion"
        self.ws.append(COLUMNAS)

    def agregar_fila(self, estado: dict) -> None:
        self.ws.append([_celda(estado.get(col)) for col in COLUMNAS])

    def escribir_parametros(self, parametros: dict) -> None:
        _escribir_parametros(self.wb, parametros)

    def guardar(self) -> Path:
        self.ruta.parent.mkdir(parents=True, exist_ok=True)
        self.wb.save(self.ruta)
        return self.ruta


def leer_filas(ruta_archivo: str | Path) -> list[dict]:
    """Lee el .xlsx y devuelve una lista de dicts (una por fila de datos)."""
    wb = load_workbook(ruta_archivo, read_only=True, data_only=True)
    ws = wb.active
    filas = list(ws.iter_rows(values_only=True))
    wb.close()
    if not filas:
        return []
    encabezados = [str(h) if h is not None else "" for h in filas[0]]
    return [dict(zip(encabezados, fila)) for fila in filas[1:]]


def exportar_resultados(
    filas: list[dict],
    ruta_archivo: str,
    parametros: dict | None = None,
) -> Path:
    """
    Alternativa: recibe ya todas las filas y las guarda de una.
    La simulación normal usa EscritorExcel (append por evento).
    """
    escritor = EscritorExcel(ruta_archivo)
    for estado in filas:
        escritor.agregar_fila(estado)
    if parametros:
        _escribir_parametros(escritor.wb, parametros)
    return escritor.guardar()


def _escribir_parametros(wb: Workbook, parametros: dict) -> None:
    if "Parametros" in wb.sheetnames:
        ws = wb["Parametros"]
    else:
        ws = wb.create_sheet("Parametros")
    ws.delete_rows(1, ws.max_row)
    ws.append(["clave", "valor"])
    for clave, valor in parametros.items():
        ws.append([clave, _celda(valor)])


def _celda(valor):
    """None → celda vacía."""
    return "" if valor is None else valor
