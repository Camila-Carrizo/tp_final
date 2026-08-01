"""
ui.py
-----
Interfaz Tkinter:
  1. Pedir parámetros al usuario
  2. Ejecutar la simulación (genera Excel)
  3. Mostrar las filas leídas del Excel
"""

from __future__ import annotations

import os
import subprocess
import sys
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from excel import COLUMNAS, leer_filas
from parametros import crear_parametros
from simulador import ejecutar

RUTA_EXCEL_DEFAULT = Path(__file__).resolve().parent / "salida" / "simulacion.xlsx"


def _mostrar_celda(valor) -> str:
    """None / vacío → '-' en la grilla."""
    if valor is None or valor == "" or valor == "None":
        return "-"
    return str(valor)


def lanzar_interfaz(ruta_excel: str | Path | None = None) -> None:
    """Abre la ventana: formulario de parámetros + tabla de resultados."""
    App(ruta_excel_inicial=ruta_excel).run()


class App:
    def __init__(self, ruta_excel_inicial: str | Path | None = None):
        self.root = tk.Tk()
        self.root.title("Simulación ascensor — Ejercicio 124")
        self.root.geometry("1200x700")
        self.ruta_excel = Path(ruta_excel_inicial) if ruta_excel_inicial else RUTA_EXCEL_DEFAULT
        self.vars: dict[str, tk.Variable] = {}
        self.entries: dict[str, ttk.Entry] = {}
        self._build()

    def run(self) -> None:
        self.root.mainloop()

    def _build(self) -> None:
        defaults = crear_parametros()

        paned = ttk.Panedwindow(self.root, orient=tk.VERTICAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        form = ttk.LabelFrame(paned, text="Parámetros", padding=10)
        paned.add(form, weight=0)

        resultados = ttk.LabelFrame(paned, text="Resultados (desde Excel)", padding=8)
        paned.add(resultados, weight=1)

        self._build_form(form, defaults)
        self._build_resultados(resultados)
        # No cargar ni simular al abrir: solo al apretar "Ejecutar simulación"

    def _build_form(self, parent: ttk.LabelFrame, defaults: dict) -> None:
        # --- Simulación ---
        g1 = ttk.LabelFrame(parent, text="Simulación", padding=8)
        g1.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=(0, 8))

        self._campo(g1, 0, "cantidad_eventos", "Cantidad de eventos", defaults["cantidad_eventos"])
        self._campo(g1, 1, "semilla", "Semilla (vacío = aleatorio)", defaults["semilla"] or "")

        # --- Ascensor / tiempos ---
        g2 = ttk.LabelFrame(parent, text="Ascensor y tiempos (segundos)", padding=8)
        g2.grid(row=0, column=1, sticky="nsew", padx=(0, 8), pady=(0, 8))

        self._campo(g2, 0, "capacidad", "Capacidad", defaults["capacidad"])
        self._campo(g2, 1, "tiempo_espera_e", "Tiempo espera E", defaults["tiempo_espera_e"])
        self._campo(g2, 2, "tiempo_descenso_d", "Tiempo descenso D", defaults["tiempo_descenso_d"])
        self._campo(g2, 3, "tiempo_ascenso_a", "Tiempo ascenso A", defaults["tiempo_ascenso_a"])
        self._campo(g2, 4, "media_llegada_pasajero", "Media llegada pasajero (Exp)", defaults["media_llegada_pasajero"])
        self._campo(g2, 5, "probabilidad_bajar", "Prob. bajar (0-1)", defaults["probabilidad_bajar"])
        self._campo(g2, 6, "viaje_min", "Viaje min U(a,b)", defaults["viaje_min"])
        self._campo(g2, 7, "viaje_max", "Viaje max U(a,b)", defaults["viaje_max"])

        # --- Condiciones iniciales ---
        g3 = ttk.LabelFrame(parent, text="Condiciones iniciales", padding=8)
        g3.grid(row=0, column=2, sticky="nsew", pady=(0, 8))

        self.vars["sin_condiciones"] = tk.BooleanVar(value=False)
        chk = ttk.Checkbutton(
            g3,
            text="Arranque de cero (H vacío)",
            variable=self.vars["sin_condiciones"],
            command=self._toggle_condiciones,
        )
        chk.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 6))

        self._campo(g3, 1, "H", "H (a bordo; P se calcula)", defaults["H"])
        self._campo(g3, 2, "cola_bajan", "Cola bajan", defaults["cola_bajan"])
        self._campo(g3, 3, "cola_suben", "Cola suben", defaults["cola_suben"])

        ttk.Label(g3, text="Dirección ascensor").grid(row=4, column=0, sticky="w", pady=2)
        self.vars["direccion_ascensor"] = tk.StringVar(value=defaults["direccion_ascensor"])
        ttk.Combobox(
            g3,
            textvariable=self.vars["direccion_ascensor"],
            values=("sube", "baja"),
            state="readonly",
            width=12,
        ).grid(row=4, column=1, sticky="w", pady=2)

        # --- Acciones ---
        acciones = ttk.Frame(parent)
        acciones.grid(row=1, column=0, columnspan=3, sticky="ew")

        ttk.Button(acciones, text="Restaurar defaults", command=self._restaurar_defaults).pack(
            side=tk.LEFT
        )
        ttk.Button(acciones, text="Ejecutar simulación", command=self._ejecutar).pack(
            side=tk.RIGHT, padx=(8, 0)
        )
        ttk.Button(acciones, text="Abrir Excel", command=self._abrir_excel).pack(side=tk.RIGHT)

        self.lbl_estado = ttk.Label(acciones, text="")
        self.lbl_estado.pack(side=tk.RIGHT, padx=12)

        parent.columnconfigure(0, weight=1)
        parent.columnconfigure(1, weight=1)
        parent.columnconfigure(2, weight=1)

    def _campo(self, parent, fila: int, clave: str, etiqueta: str, valor) -> None:
        ttk.Label(parent, text=etiqueta).grid(row=fila, column=0, sticky="w", pady=2, padx=(0, 8))
        var = tk.StringVar(value="" if valor is None else str(valor))
        self.vars[clave] = var
        entry = ttk.Entry(parent, textvariable=var, width=14)
        entry.grid(row=fila, column=1, sticky="w", pady=2)
        self.entries[clave] = entry

    def _build_resultados(self, parent: ttk.LabelFrame) -> None:
        top = ttk.Frame(parent)
        top.pack(fill=tk.X, pady=(0, 6))
        self.lbl_ruta = ttk.Label(top, text="Sin resultados todavía")
        self.lbl_ruta.pack(side=tk.LEFT, fill=tk.X, expand=True)

        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(frame, columns=COLUMNAS, show="headings")
        for col in COLUMNAS:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, stretch=False)

        scroll_y = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.tree.yview)
        scroll_x = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

    def _toggle_condiciones(self) -> None:
        deshabilitar = self.vars["sin_condiciones"].get()
        estado = tk.DISABLED if deshabilitar else tk.NORMAL
        for clave in ("H", "cola_bajan", "cola_suben"):
            if clave in self.entries:
                self.entries[clave].configure(state=estado)
        if deshabilitar:
            self.lbl_estado.configure(text="Modo: arranque de cero (sin H/colas iniciales)")
        else:
            self.lbl_estado.configure(text="")

    def _restaurar_defaults(self) -> None:
        defaults = crear_parametros()
        self.vars["sin_condiciones"].set(False)
        for clave, valor in defaults.items():
            if clave in self.vars and isinstance(self.vars[clave], tk.StringVar):
                self.vars[clave].set("" if valor is None else str(valor))
        self.vars["direccion_ascensor"].set(defaults["direccion_ascensor"])
        self.lbl_estado.configure(text="Defaults restaurados")

    def _leer_parametros(self) -> dict:
        """Arma el dict compatible con crear_parametros / ejecutar."""
        def entero(clave: str) -> int:
            return int(self.vars[clave].get().strip())

        def flotante(clave: str) -> float:
            return float(self.vars[clave].get().strip().replace(",", "."))

        semilla_txt = self.vars["semilla"].get().strip()
        semilla = int(semilla_txt) if semilla_txt else None

        if self.vars["sin_condiciones"].get():
            h = None
            cola_bajan = 0
            cola_suben = 0
        else:
            h = entero("H")
            cola_bajan = entero("cola_bajan")
            cola_suben = entero("cola_suben")

        viaje_min = flotante("viaje_min")
        viaje_max = flotante("viaje_max")
        if viaje_min > viaje_max:
            raise ValueError("viaje_min no puede ser mayor que viaje_max")

        prob = flotante("probabilidad_bajar")
        if not 0.0 <= prob <= 1.0:
            raise ValueError("probabilidad_bajar debe estar entre 0 y 1")

        capacidad = entero("capacidad")
        if capacidad <= 0:
            raise ValueError("capacidad debe ser > 0")
        if h is not None and h > capacidad:
            raise ValueError("H no puede ser mayor que la capacidad")

        return crear_parametros(
            cantidad_eventos=entero("cantidad_eventos"),
            capacidad=capacidad,
            tiempo_espera_e=flotante("tiempo_espera_e"),
            tiempo_descenso_d=flotante("tiempo_descenso_d"),
            tiempo_ascenso_a=flotante("tiempo_ascenso_a"),
            media_llegada_pasajero=flotante("media_llegada_pasajero"),
            probabilidad_bajar=prob,
            viaje_min=viaje_min,
            viaje_max=viaje_max,
            H=h,
            direccion_ascensor=self.vars["direccion_ascensor"].get(),
            cola_bajan=cola_bajan,
            cola_suben=cola_suben,
            semilla=semilla,
        )

    def _ejecutar(self) -> None:
        try:
            parametros = self._leer_parametros()
        except ValueError as exc:
            messagebox.showerror("Parámetros inválidos", str(exc))
            return
        except Exception as exc:
            messagebox.showerror("Parámetros inválidos", f"Revisá los valores.\n{exc}")
            return

        self.lbl_estado.configure(text="Simulando...")
        self.root.update_idletasks()

        try:
            _estado, ruta = ejecutar(parametros=parametros, ruta_excel=self.ruta_excel)
            self.ruta_excel = Path(ruta) if ruta else self.ruta_excel
            self._cargar_excel(self.ruta_excel)
            self.lbl_estado.configure(text=f"Listo — {self.ruta_excel.name}")
        except Exception as exc:
            messagebox.showerror("Error en la simulación", str(exc))
            self.lbl_estado.configure(text="Error")

    def _cargar_excel(self, ruta: Path) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)
        if not ruta.exists():
            self.lbl_ruta.configure(text="Sin archivo")
            return
        filas = leer_filas(ruta)
        for fila in filas:
            self.tree.insert(
                "",
                tk.END,
                values=[_mostrar_celda(fila.get(col)) for col in COLUMNAS],
            )
        self.lbl_ruta.configure(text=f"{ruta}  ({len(filas)} filas)")

    def _abrir_excel(self) -> None:
        ruta = self.ruta_excel
        if ruta is None or not ruta.exists():
            messagebox.showwarning("Sin archivo", "Todavía no hay Excel. Ejecutá la simulación.")
            return
        try:
            if sys.platform.startswith("win"):
                os.startfile(ruta)  # type: ignore[attr-defined]
            elif sys.platform == "darwin":
                subprocess.run(["open", str(ruta)], check=False)
            else:
                subprocess.run(["xdg-open", str(ruta)], check=False)
        except Exception as exc:
            messagebox.showerror("No se pudo abrir", str(exc))
