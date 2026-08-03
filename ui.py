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
import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from excel import (
    COLORES_ENCABEZADO,
    COLUMNAS,
    caracteres_columna,
    leer_filas,
    titulo_columna,
)
from parametros import crear_parametros
from simulador import ejecutar

RUTA_EXCEL_DEFAULT = Path(__file__).resolve().parent / "salida" / "simulacion.xlsx"
# ~ px por carácter en Segoe UI 8 + padding
PX_POR_CHAR = 8
PADDING_COL_PX = 24
# ttk.Treeview se congela con demasiadas filas; el Excel igual tiene todo el rango
MAX_FILAS_UI = 2000
LOTE_UI = 80
SPINNER_FRAMES = ("⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏")


def _ancho_px(clave: str) -> int:
    return caracteres_columna(clave) * PX_POR_CHAR + PADDING_COL_PX


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
        self._simulando = False
        self._spinner_after_id = None
        self._spinner_idx = 0
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
        self._campo(g1, 1, "mostrar_desde", "Mostrar desde fila", defaults["mostrar_desde"])
        self._campo(g1, 2, "mostrar_hasta", "Mostrar hasta fila", defaults["mostrar_hasta"])
        self._campo(g1, 3, "semilla", "Semilla (vacío = aleatorio)", defaults["semilla"] or "")

        # --- Ascensor / tiempos ---
        g2 = ttk.LabelFrame(parent, text="Distribuciones (segundos)", padding=8)
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

        self.btn_defaults = ttk.Button(
            acciones, text="Restaurar defaults", command=self._restaurar_defaults
        )
        self.btn_defaults.pack(side=tk.LEFT)
        self.btn_ejecutar = ttk.Button(
            acciones, text="Ejecutar simulación", command=self._ejecutar
        )
        self.btn_ejecutar.pack(side=tk.RIGHT, padx=(8, 0))
        self.btn_abrir_excel = ttk.Button(
            acciones, text="Abrir Excel", command=self._abrir_excel
        )
        self.btn_abrir_excel.pack(side=tk.RIGHT)

        self.lbl_spinner = ttk.Label(acciones, text="", width=2)
        self.lbl_spinner.pack(side=tk.RIGHT, padx=(4, 0))
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

        # Resultado pedido por el enunciado (solo UI, no Excel)
        caja = ttk.LabelFrame(parent, text="Resultado del ejercicio", padding=10)
        caja.pack(fill=tk.X, pady=(0, 8))
        self.lbl_permanencia = tk.Label(
            caja,
            text="TIEMPO DE PERMANENCIA EN PISO 15: —",
            font=("Segoe UI", 13, "bold"),
            fg="#008C00",
            anchor="w",
        )
        self.lbl_permanencia.pack(anchor="w", fill=tk.X)

        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True)

        # Encabezados coloreados (mismos grupos que el Excel)
        self.header_canvas = tk.Canvas(frame, height=44, highlightthickness=0)
        self._header_inner = tk.Frame(self.header_canvas)
        self.header_canvas.create_window((0, 0), window=self._header_inner, anchor="nw")
        for col in COLUMNAS:
            color = COLORES_ENCABEZADO.get(col, "D9D2E9")
            w = _ancho_px(col)
            celda = tk.Frame(self._header_inner, width=w, height=40, bg=f"#{color}")
            celda.pack_propagate(False)
            celda.pack(side=tk.LEFT, fill=tk.Y)
            tk.Label(
                celda,
                text=titulo_columna(col),
                bg=f"#{color}",
                fg="#333333",
                font=("Segoe UI", 8, "bold"),
                justify="center",
                wraplength=w - 6,
            ).pack(expand=True, fill=tk.BOTH)

        # show="" = sin headings nativos (usamos la barra de colores de arriba)
        self.tree = ttk.Treeview(frame, columns=COLUMNAS, show="", height=12)
        for col in COLUMNAS:
            self.tree.column(
                col, width=_ancho_px(col), stretch=False, anchor="center"
            )

        scroll_y = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.tree.yview)
        self._hbar = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=self._scroll_x)
        self.tree.configure(
            yscrollcommand=scroll_y.set,
            xscrollcommand=self._sync_x_desde_tree,
        )
        self._header_inner.bind("<Configure>", self._actualizar_scroll_header)

        self.header_canvas.grid(row=0, column=0, sticky="ew")
        self.tree.grid(row=1, column=0, sticky="nsew")
        scroll_y.grid(row=1, column=1, sticky="ns")
        self._hbar.grid(row=2, column=0, sticky="ew")
        frame.rowconfigure(1, weight=1)
        frame.columnconfigure(0, weight=1)

    def _actualizar_scroll_header(self, _event=None) -> None:
        self.header_canvas.configure(scrollregion=self.header_canvas.bbox("all"))

    def _scroll_x(self, *args) -> None:
        self.tree.xview(*args)
        self.header_canvas.xview(*args)

    def _sync_x_desde_tree(self, first, last) -> None:
        self._hbar.set(first, last)
        self.header_canvas.xview_moveto(first)

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
        etiquetas = {
            "cantidad_eventos": "Cantidad de eventos",
            "mostrar_desde": "Mostrar desde fila",
            "mostrar_hasta": "Mostrar hasta fila",
            "semilla": "Semilla",
            "capacidad": "Capacidad",
            "tiempo_espera_e": "Tiempo espera E",
            "tiempo_descenso_d": "Tiempo descenso D",
            "tiempo_ascenso_a": "Tiempo ascenso A",
            "media_llegada_pasajero": "Media llegada pasajero",
            "probabilidad_bajar": "Prob. bajar",
            "viaje_min": "Viaje min",
            "viaje_max": "Viaje max",
            "H": "H",
            "cola_bajan": "Cola bajan",
            "cola_suben": "Cola suben",
        }

        def _texto(clave: str) -> str:
            return self.vars[clave].get().strip().replace(",", ".")

        def entero(clave: str, *, minimo: int | None = None) -> int:
            nombre = etiquetas.get(clave, clave)
            txt = _texto(clave)
            if txt == "":
                raise ValueError(f"{nombre}: no puede estar vacío")
            try:
                # Acepta "5" o "5.0" pero no "5.5"
                valor_f = float(txt)
            except ValueError as exc:
                raise ValueError(f"{nombre}: debe ser un número entero") from exc
            if not valor_f.is_integer():
                raise ValueError(f"{nombre}: debe ser un número entero (sin decimales)")
            valor = int(valor_f)
            if minimo is not None and valor < minimo:
                raise ValueError(f"{nombre}: debe ser >= {minimo}")
            return valor

        def flotante(
            clave: str,
            *,
            minimo: float | None = None,
            minimo_estricto: bool = False,
        ) -> float:
            nombre = etiquetas.get(clave, clave)
            txt = _texto(clave)
            if txt == "":
                raise ValueError(f"{nombre}: no puede estar vacío")
            try:
                valor = float(txt)
            except ValueError as exc:
                raise ValueError(f"{nombre}: debe ser un número") from exc
            if minimo is not None:
                if minimo_estricto and valor <= minimo:
                    raise ValueError(f"{nombre}: debe ser > {minimo}")
                if not minimo_estricto and valor < minimo:
                    raise ValueError(f"{nombre}: debe ser >= {minimo}")
            return valor

        # Semilla opcional
        semilla_txt = _texto("semilla")
        if semilla_txt == "":
            semilla = None
        else:
            try:
                semilla_f = float(semilla_txt)
            except ValueError as exc:
                raise ValueError("Semilla: debe ser un número entero") from exc
            if not semilla_f.is_integer():
                raise ValueError("Semilla: debe ser un número entero (sin decimales)")
            semilla = int(semilla_f)

        cantidad_eventos = entero("cantidad_eventos", minimo=1)
        mostrar_desde = entero("mostrar_desde", minimo=1)
        mostrar_hasta = entero("mostrar_hasta", minimo=1)
        if mostrar_desde > mostrar_hasta:
            raise ValueError("Mostrar desde no puede ser mayor que mostrar hasta")
        if mostrar_hasta > cantidad_eventos:
            raise ValueError(
                "Mostrar hasta no puede ser mayor que la cantidad de eventos"
            )
        capacidad = entero("capacidad", minimo=1)

        tiempo_espera_e = flotante("tiempo_espera_e", minimo=0, minimo_estricto=True)
        tiempo_descenso_d = flotante("tiempo_descenso_d", minimo=0, minimo_estricto=True)
        tiempo_ascenso_a = flotante("tiempo_ascenso_a", minimo=0, minimo_estricto=True)
        media_llegada = flotante(
            "media_llegada_pasajero", minimo=0, minimo_estricto=True
        )

        prob = flotante("probabilidad_bajar", minimo=0)
        if prob > 1.0:
            raise ValueError("Prob. bajar: debe estar entre 0 y 1")

        viaje_min = flotante("viaje_min", minimo=0)
        viaje_max = flotante("viaje_max", minimo=0)
        if viaje_min > viaje_max:
            raise ValueError("Viaje min no puede ser mayor que Viaje max")

        if self.vars["sin_condiciones"].get():
            h = None
            cola_bajan = 0
            cola_suben = 0
        else:
            h = entero("H", minimo=0)
            if h > capacidad:
                raise ValueError("H no puede ser mayor que la capacidad")
            cola_bajan = entero("cola_bajan", minimo=0)
            cola_suben = entero("cola_suben", minimo=0)

        direccion = self.vars["direccion_ascensor"].get()
        if direccion not in ("sube", "baja"):
            raise ValueError("Dirección ascensor: debe ser 'sube' o 'baja'")

        return crear_parametros(
            cantidad_eventos=cantidad_eventos,
            mostrar_desde=mostrar_desde,
            mostrar_hasta=mostrar_hasta,
            capacidad=capacidad,
            tiempo_espera_e=tiempo_espera_e,
            tiempo_descenso_d=tiempo_descenso_d,
            tiempo_ascenso_a=tiempo_ascenso_a,
            media_llegada_pasajero=media_llegada,
            probabilidad_bajar=prob,
            viaje_min=viaje_min,
            viaje_max=viaje_max,
            H=h,
            direccion_ascensor=direccion,
            cola_bajan=cola_bajan,
            cola_suben=cola_suben,
            semilla=semilla,
        )

    def _set_ui_ocupada(self, ocupada: bool) -> None:
        estado = tk.DISABLED if ocupada else tk.NORMAL
        self.btn_ejecutar.configure(state=estado)
        self.btn_defaults.configure(state=estado)
        self.btn_abrir_excel.configure(state=estado)
        if ocupada:
            self._iniciar_spinner()
        else:
            self._detener_spinner()

    def _iniciar_spinner(self) -> None:
        self._detener_spinner()
        self._spinner_idx = 0
        self._tick_spinner()

    def _tick_spinner(self) -> None:
        self.lbl_spinner.configure(text=SPINNER_FRAMES[self._spinner_idx])
        self._spinner_idx = (self._spinner_idx + 1) % len(SPINNER_FRAMES)
        self._spinner_after_id = self.root.after(80, self._tick_spinner)

    def _detener_spinner(self) -> None:
        if self._spinner_after_id is not None:
            self.root.after_cancel(self._spinner_after_id)
            self._spinner_after_id = None
        self.lbl_spinner.configure(text="")

    def _ejecutar(self) -> None:
        if self._simulando:
            return
        try:
            parametros = self._leer_parametros()
        except ValueError as exc:
            messagebox.showerror("Parámetros inválidos", str(exc))
            return
        except Exception as exc:
            messagebox.showerror("Parámetros inválidos", f"Revisá los valores.\n{exc}")
            return

        self._simulando = True
        self._set_ui_ocupada(True)
        self.lbl_estado.configure(text="Simulando...")
        hijos = self.tree.get_children()
        if hijos:
            self.tree.delete(*hijos)
        self.lbl_ruta.configure(text="Generando Excel...")
        self.lbl_permanencia.configure(text="TIEMPO DE PERMANENCIA EN PISO 15: —")

        ruta_excel = self.ruta_excel

        def worker() -> None:
            try:
                estado, ruta = ejecutar(parametros=parametros, ruta_excel=ruta_excel)
                # Leer Excel acá (hilo) para no congelar la UI
                filas = leer_filas(ruta) if ruta else []
                self.root.after(
                    0, lambda: self._fin_simulacion_ok(estado, ruta, filas)
                )
            except Exception as exc:
                self.root.after(0, lambda e=exc: self._fin_simulacion_error(e))

        threading.Thread(target=worker, daemon=True).start()

    def _fin_simulacion_ok(self, estado: dict, ruta, filas: list) -> None:
        try:
            self.ruta_excel = Path(ruta) if ruta else self.ruta_excel
            self._mostrar_permanencia(estado.get("ACUMULADOR_PERMANENCIA"))
            self.lbl_estado.configure(text="Cargando tabla...")
            self._iniciar_carga_tabla(filas)
        except Exception as exc:
            messagebox.showerror("Error al cargar resultados", str(exc))
            self.lbl_estado.configure(text="Error")
            self._simulando = False
            self._set_ui_ocupada(False)

    def _fin_simulacion_error(self, exc: Exception) -> None:
        messagebox.showerror("Error en la simulación", str(exc))
        self.lbl_estado.configure(text="Error")
        self._simulando = False
        self._set_ui_ocupada(False)

    def _iniciar_carga_tabla(self, filas: list) -> None:
        """Inserta filas en lotes para que la ventana no deje de responder."""
        hijos = self.tree.get_children()
        if hijos:
            self.tree.delete(*hijos)

        total_excel = len(filas)
        if total_excel > MAX_FILAS_UI:
            messagebox.showinfo(
                "Muchas filas",
                f"El Excel tiene {total_excel} filas.\n"
                f"Solo se muestran las últimas {MAX_FILAS_UI}.",
            )
            filas = filas[-MAX_FILAS_UI:]

        self._filas_carga = filas
        self._filas_carga_idx = 0
        self._filas_carga_total_excel = total_excel
        self._insertar_lote_tabla()

    def _insertar_lote_tabla(self) -> None:
        filas = self._filas_carga
        inicio = self._filas_carga_idx
        fin = min(inicio + LOTE_UI, len(filas))
        for i in range(inicio, fin):
            fila = filas[i]
            self.tree.insert(
                "",
                tk.END,
                values=[_mostrar_celda(fila.get(col)) for col in COLUMNAS],
            )
        self._filas_carga_idx = fin

        if fin < len(filas):
            self.lbl_estado.configure(text=f"Cargando tabla... {fin}/{len(filas)}")
            self.root.after(1, self._insertar_lote_tabla)
            return

        mostradas = len(filas)
        total = self._filas_carga_total_excel
        if mostradas < total:
            self.lbl_ruta.configure(
                text=f"{self.ruta_excel}  (últimas {mostradas} en tabla / {total} en Excel)"
            )
        else:
            self.lbl_ruta.configure(text=f"{self.ruta_excel}  ({total} filas)")
        self.lbl_estado.configure(text=f"Listo — {self.ruta_excel.name}")
        self._simulando = False
        self._set_ui_ocupada(False)

    def _mostrar_permanencia(self, segundos) -> None:
        if segundos is None:
            texto = "TIEMPO DE PERMANENCIA EN PISO 15: —"
        else:
            # Mostrar sin decimales innecesarios (ya viene truncado del simulador)
            valor = float(segundos)
            if valor.is_integer():
                mostrado = str(int(valor))
            else:
                mostrado = str(valor)
            texto = f"TIEMPO DE PERMANENCIA EN PISO 15: {mostrado} segs"
        self.lbl_permanencia.configure(text=texto)

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
