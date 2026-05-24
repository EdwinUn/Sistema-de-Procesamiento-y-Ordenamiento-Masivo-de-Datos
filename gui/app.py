from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import List, Optional

from config.settings import ARCHIVO_POR_DEFECTO
from libs.ordenamiento_interno import (
    ResultadoBusqueda,
    ResultadoOrden,
    busqueda_binaria,
    busqueda_lineal,
    ordenar_interno,
)
from libs.ordenamiento_externo import ordenar_externo
from utils.file_handler import cargar_datos, exportar_resultados

# ── Paleta de colores ─────────────────────────────────────────────────────────
BG          = "#F0F4F8"
HEADER_BG   = "#1E2D40"
HEADER_SUB  = "#7A92A9"
PANEL       = "#FFFFFF"
BORDER      = "#D1D9E0"
TEXT        = "#1F2937"
TEXT2       = "#6B7280"
ACCENT      = "#2563EB"   # azul  — botones archivo
GREEN       = "#059669"   # verde — ordenar
PURPLE      = "#7C3AED"   # violeta — buscar
RED         = "#DC2626"   # rojo — salir
OUT_BG      = "#0F172A"   # fondo consola (oscuro)
OUT_FG      = "#CBD5E1"   # texto consola
ST_OK_BG    = "#DCFCE7"
ST_OK_FG    = "#166534"
ST_ERR_BG   = "#FEE2E2"
ST_ERR_FG   = "#991B1B"
ST_INF_BG   = "#DBEAFE"
ST_INF_FG   = "#1E40AF"


class DataApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Sistema de Procesamiento y Ordenamiento Masivo de Datos")
        self.geometry("1120x720")
        self.resizable(False, False)
        self.configure(bg=BG)

        self.datos: List[float] = []
        self.resultado_orden: Optional[ResultadoOrden] = None
        self.resultado_busqueda: Optional[ResultadoBusqueda] = None

        self.sort_type       = tk.StringVar(value="interno")
        self.sort_method     = tk.StringVar(value="bubble")
        self.sort_method_ext = tk.StringVar(value="directa")
        self.sort_order      = tk.StringVar(value="asc")
        self.search_type     = tk.StringVar(value="lineal")
        self.chunk_size      = tk.StringVar(value="100")
        self.search_value    = tk.StringVar()

        self._configurar_estilos()
        self._crear_componentes()
        self._actualizar_estado("Listo. Cargue un archivo TXT o XLSX para comenzar.", "info")

    # ── Estilos ───────────────────────────────────────────────────────────────

    def _configurar_estilos(self) -> None:
        s = ttk.Style(self)
        s.theme_use("clam")

        s.configure("TFrame",       background=BG)
        s.configure("TLabel",       background=BG,    foreground=TEXT, font=("Segoe UI", 9))
        s.configure("TRadiobutton", background=PANEL, foreground=TEXT, font=("Segoe UI", 9))
        s.map("TRadiobutton",       background=[("active", PANEL)])
        s.configure("TCombobox",    font=("Segoe UI", 9))
        s.configure("TEntry",       font=("Segoe UI", 9))

        def _btn(name, bg, hover, press):
            s.configure(f"{name}.TButton",
                        background=bg, foreground="#FFFFFF",
                        font=("Segoe UI", 9, "bold"),
                        padding=(10, 6), relief="flat", borderwidth=0)
            s.map(f"{name}.TButton",
                  background=[("active", hover), ("pressed", press)],
                  foreground=[("active", "#FFFFFF")])

        _btn("Blue",   ACCENT,  "#1D4ED8", "#1E40AF")
        _btn("Green",  GREEN,   "#047857", "#065F46")
        _btn("Purple", PURPLE,  "#6D28D9", "#5B21B6")
        _btn("Red",    RED,     "#B91C1C", "#991B1B")
        _btn("Gray",   "#4B5563","#374151","#1F2937")

    # ── Layout principal ──────────────────────────────────────────────────────

    def _crear_componentes(self) -> None:
        # Header
        self._hacer_header()

        # Cuerpo de dos columnas
        body = tk.Frame(self, bg=BG)
        body.grid(row=1, column=0, sticky="nsew", padx=14, pady=(12, 0))
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        body.columnconfigure(0, minsize=310, weight=0)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        left  = tk.Frame(body, bg=BG)
        left.grid(row=0, column=0, sticky="ns", padx=(0, 10))
        right = tk.Frame(body, bg=BG)
        right.grid(row=0, column=1, sticky="nsew")
        right.rowconfigure(1, weight=1)
        right.columnconfigure(0, weight=1)

        self._hacer_panel_archivo(left)
        self._hacer_panel_ordenamiento(left)
        self._hacer_panel_busqueda(left)
        self._hacer_panel_salida(right)

        # Barra de estado
        self._estado_frame = tk.Frame(self, bg=ST_OK_BG, height=30)
        self._estado_frame.grid(row=2, column=0, sticky="ew")
        self._estado_frame.grid_propagate(False)
        self._estado_label = tk.Label(
            self._estado_frame, text="", bg=ST_OK_BG, fg=ST_OK_FG,
            font=("Segoe UI", 9), anchor="w", padx=16,
        )
        self._estado_label.pack(side="left", fill="both", expand=True)

        self._actualizar_opciones_ordenamiento()

    def _hacer_header(self) -> None:
        hdr = tk.Frame(self, bg=HEADER_BG, height=64)
        hdr.grid(row=0, column=0, sticky="ew")
        hdr.grid_propagate(False)
        tk.Label(hdr, text="Sistema de Procesamiento y Ordenamiento Masivo de Datos",
                 bg=HEADER_BG, fg="#FFFFFF", font=("Segoe UI", 13, "bold")).place(x=18, y=10)
        tk.Label(hdr, text="Ordenamiento interno y externo  |  Busqueda secuencial y binaria  |  Exportacion TXT / XLSX",
                 bg=HEADER_BG, fg=HEADER_SUB, font=("Segoe UI", 8)).place(x=20, y=38)

    # ── Tarjetas del panel izquierdo ──────────────────────────────────────────

    def _tarjeta(self, parent: tk.Frame, titulo: str) -> tk.Frame:
        """Crea un contenedor con borde y título de sección."""
        outer = tk.Frame(parent, bg=BORDER, bd=0)
        outer.pack(fill="x", pady=(0, 8))
        inner = tk.Frame(outer, bg=PANEL, bd=0)
        inner.pack(fill="x", padx=1, pady=1)
        tk.Label(inner, text=titulo, bg=PANEL, fg=TEXT2,
                 font=("Segoe UI", 7, "bold")).pack(anchor="w", padx=12, pady=(8, 4))
        sep = tk.Frame(inner, bg=BORDER, height=1)
        sep.pack(fill="x", padx=12, pady=(0, 8))
        return inner

    def _hacer_panel_archivo(self, parent: tk.Frame) -> None:
        card = self._tarjeta(parent, "ARCHIVO")

        row1 = tk.Frame(card, bg=PANEL)
        row1.pack(fill="x", padx=12, pady=2)
        ttk.Button(row1, text="Cargar archivo",
                   style="Blue.TButton", command=self._cargar_archivo
                   ).pack(side="left", fill="x", expand=True, padx=(0, 4))
        ttk.Button(row1, text="Exportar",
                   style="Blue.TButton", command=self._exportar_resultados
                   ).pack(side="left", fill="x", expand=True)

        row2 = tk.Frame(card, bg=PANEL)
        row2.pack(fill="x", padx=12, pady=(2, 10))
        ttk.Button(row2, text="Mostrar resultados",
                   style="Gray.TButton", command=self._mostrar_resultados
                   ).pack(side="left", fill="x", expand=True, padx=(0, 4))
        ttk.Button(row2, text="Salir",
                   style="Red.TButton", command=self.quit
                   ).pack(side="left", fill="x", expand=True)

    def _hacer_panel_ordenamiento(self, parent: tk.Frame) -> None:
        card = self._tarjeta(parent, "ORDENAMIENTO")

        # Tipo de ordenamiento + orden (misma fila)
        f_tipo = tk.Frame(card, bg=PANEL)
        f_tipo.pack(fill="x", padx=12, pady=2)
        tk.Label(f_tipo, text="Tipo:", bg=PANEL, fg=TEXT2,
                 font=("Segoe UI", 8), width=7, anchor="w").pack(side="left")
        ttk.Radiobutton(f_tipo, text="Interno", variable=self.sort_type, value="interno",
                        command=self._actualizar_opciones_ordenamiento).pack(side="left")
        ttk.Radiobutton(f_tipo, text="Externo", variable=self.sort_type, value="externo",
                        command=self._actualizar_opciones_ordenamiento).pack(side="left", padx=(4, 12))
        tk.Frame(f_tipo, bg=BORDER, width=1, height=16).pack(side="left", padx=6)
        tk.Label(f_tipo, text="Orden:", bg=PANEL, fg=TEXT2,
                 font=("Segoe UI", 8)).pack(side="left", padx=(6, 4))
        ttk.Radiobutton(f_tipo, text="Asc", variable=self.sort_order, value="asc").pack(side="left")
        ttk.Radiobutton(f_tipo, text="Desc", variable=self.sort_order, value="desc").pack(side="left", padx=4)

        # Método interno
        f_met = tk.Frame(card, bg=PANEL)
        f_met.pack(fill="x", padx=12, pady=4)
        tk.Label(f_met, text="M. interno:", bg=PANEL, fg=TEXT,
                 font=("Segoe UI", 9), width=11, anchor="w").pack(side="left")
        self._metodo_combo = ttk.Combobox(
            f_met, textvariable=self.sort_method,
            values=["bubble","selection","insertion","shell",
                    "merge","quick","heap","counting","radix"],
            state="readonly", width=17,
        )
        self._metodo_combo.pack(side="left")

        # Método externo
        f_ext = tk.Frame(card, bg=PANEL)
        f_ext.pack(fill="x", padx=12, pady=4)
        tk.Label(f_ext, text="M. externo:", bg=PANEL, fg=TEXT,
                 font=("Segoe UI", 9), width=11, anchor="w").pack(side="left")
        self._metodo_ext_combo = ttk.Combobox(
            f_ext, textvariable=self.sort_method_ext,
            values=["directa","natural","equilibrada","polifasica","sustitucion"],
            state="readonly", width=17,
        )
        self._metodo_ext_combo.pack(side="left")

        # Chunk size
        f_chunk = tk.Frame(card, bg=PANEL)
        f_chunk.pack(fill="x", padx=12, pady=4)
        tk.Label(f_chunk, text="Chunk size:", bg=PANEL, fg=TEXT,
                 font=("Segoe UI", 9), width=11, anchor="w").pack(side="left")
        self._chunk_entry = ttk.Entry(f_chunk, textvariable=self.chunk_size, width=10)
        self._chunk_entry.pack(side="left")

        ttk.Button(card, text="Ordenar datos", style="Green.TButton",
                   command=self._ordenar_datos
                   ).pack(fill="x", padx=12, pady=(6, 12))

    def _hacer_panel_busqueda(self, parent: tk.Frame) -> None:
        card = self._tarjeta(parent, "BUSQUEDA")

        f_val = tk.Frame(card, bg=PANEL)
        f_val.pack(fill="x", padx=12, pady=2)
        tk.Label(f_val, text="Valor:", bg=PANEL, fg=TEXT,
                 font=("Segoe UI", 9), width=7, anchor="w").pack(side="left")
        ttk.Entry(f_val, textvariable=self.search_value, width=20).pack(side="left", fill="x", expand=True)

        f_met = tk.Frame(card, bg=PANEL)
        f_met.pack(fill="x", padx=12, pady=4)
        tk.Label(f_met, text="Metodo:", bg=PANEL, fg=TEXT2,
                 font=("Segoe UI", 8), width=7, anchor="w").pack(side="left")
        ttk.Radiobutton(f_met, text="Lineal",  variable=self.search_type, value="lineal" ).pack(side="left", padx=4)
        ttk.Radiobutton(f_met, text="Binaria", variable=self.search_type, value="binaria").pack(side="left", padx=4)

        ttk.Button(card, text="Buscar valor", style="Purple.TButton",
                   command=self._buscar_valor
                   ).pack(fill="x", padx=12, pady=(4, 12))

    def _hacer_panel_salida(self, parent: tk.Frame) -> None:
        tk.Label(parent, text="CONSOLA DE SALIDA", bg=BG, fg=TEXT2,
                 font=("Segoe UI", 7, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 4))

        output_outer = tk.Frame(parent, bg=BORDER, bd=0)
        output_outer.grid(row=1, column=0, sticky="nsew")
        parent.rowconfigure(1, weight=1)

        output_inner = tk.Frame(output_outer, bg=OUT_BG)
        output_inner.pack(fill="both", expand=True, padx=1, pady=1)
        output_inner.rowconfigure(0, weight=1)
        output_inner.columnconfigure(0, weight=1)

        self._salida_text = tk.Text(
            output_inner,
            wrap="word",
            state="disabled",
            bg=OUT_BG, fg=OUT_FG,
            font=("Consolas", 10),
            relief="flat",
            padx=16, pady=14,
            cursor="arrow",
            insertbackground=OUT_FG,
            selectbackground="#1E3A5F",
            selectforeground=OUT_FG,
        )
        self._salida_text.grid(row=0, column=0, sticky="nsew")

        sb = ttk.Scrollbar(output_inner, command=self._salida_text.yview)
        sb.grid(row=0, column=1, sticky="ns")
        self._salida_text.configure(yscrollcommand=sb.set)

    # ── Lógica de controles ───────────────────────────────────────────────────

    def _actualizar_estado(self, mensaje: str, tipo: str = "ok") -> None:
        colores = {
            "ok":    (ST_OK_BG,  ST_OK_FG),
            "error": (ST_ERR_BG, ST_ERR_FG),
            "info":  (ST_INF_BG, ST_INF_FG),
        }
        bg, fg = colores.get(tipo, colores["ok"])
        self._estado_frame.configure(bg=bg)
        self._estado_label.configure(text=f"  {mensaje}", bg=bg, fg=fg)

    def _actualizar_opciones_ordenamiento(self) -> None:
        if self.sort_type.get() == "interno":
            self._metodo_combo.configure(state="readonly")
            self._metodo_ext_combo.configure(state="disabled")
            self._chunk_entry.configure(state="disabled")
        else:
            self._metodo_combo.configure(state="disabled")
            self._metodo_ext_combo.configure(state="readonly")
            self._chunk_entry.configure(state="normal")

    def _cargar_archivo(self) -> None:
        ruta = filedialog.askopenfilename(
            title="Seleccionar archivo de datos",
            filetypes=[
                ("Archivos de datos (TXT, XLSX)", "*.txt *.xlsx"),
                ("Archivos TXT",  "*.txt"),
                ("Archivos XLSX", "*.xlsx"),
                ("Todos los archivos", "*.*"),
            ],
        )
        if not ruta:
            return
        try:
            self.datos = cargar_datos(ruta)
            self.resultado_orden = None
            self.resultado_busqueda = None
            nombre = ruta.split("/")[-1]
            self._actualizar_estado(f"Archivo cargado: {nombre}  ({len(self.datos)} valores)", "ok")
            self._mostrar_texto(
                f"Archivo cargado exitosamente\n"
                f"{'─'*46}\n"
                f"Ruta   : {ruta}\n"
                f"Valores: {len(self.datos)}\n"
                f"Min    : {min(self.datos)}\n"
                f"Max    : {max(self.datos)}\n"
            )
        except Exception as error:
            messagebox.showerror("Error al cargar archivo", str(error))
            self._actualizar_estado("Error al cargar el archivo.", "error")

    def _ordenar_datos(self) -> None:
        if not self.datos:
            messagebox.showwarning("Ordenamiento", "Debe cargar un archivo antes de ordenar.")
            return
        try:
            reversa = self.sort_order.get() == "desc"
            if self.sort_type.get() == "interno":
                metodo = self.sort_method.get()
                self.resultado_orden = ordenar_interno(self.datos, metodo=metodo, reversa=reversa)
            else:
                chunk_value = self.chunk_size.get().strip()
                if not chunk_value.isdigit() or int(chunk_value) < 1:
                    raise ValueError("El tamano de chunk debe ser un entero positivo.")
                self.resultado_orden = ordenar_externo(
                    self.datos,
                    chunk_size=int(chunk_value),
                    reversa=reversa,
                    metodo=self.sort_method_ext.get(),
                )

            r = self.resultado_orden
            orden_str = "Descendente" if reversa else "Ascendente"
            salida = (
                f"Ordenamiento completado\n"
                f"{'─'*46}\n"
                f"Algoritmo    : {r.algoritmo}\n"
                f"Orden        : {orden_str}\n"
                f"Tiempo       : {r.tiempo_ms:.3f} ms\n"
                f"Registros    : {len(r.arreglo)}\n"
                f"Comparaciones: {r.comparaciones}\n"
                f"Intercambios : {r.intercambios}\n"
            )
            if r.complejidad_t:
                salida += f"Complejidad  : {r.complejidad_t}\n"
            if r.detalles:
                salida += f"Detalles     : {r.detalles}\n"
            salida += "\n" + self._obtener_vista_previa(r.arreglo)

            self._actualizar_estado(
                f"Ordenamiento completado  |  {r.algoritmo}  |  {r.tiempo_ms:.2f} ms", "ok"
            )
            self._mostrar_texto(salida)
        except Exception as error:
            messagebox.showerror("Error de ordenamiento", str(error))
            self._actualizar_estado("Error durante el ordenamiento.", "error")

    def _buscar_valor(self) -> None:
        if not self.datos:
            messagebox.showwarning("Busqueda", "Debe cargar un archivo antes de buscar.")
            return
        valor_texto = self.search_value.get().strip()
        if not valor_texto:
            messagebox.showwarning("Busqueda", "Ingrese un valor a buscar.")
            return
        try:
            valor = float(valor_texto)
        except ValueError:
            messagebox.showerror("Busqueda", "Ingrese un numero valido.")
            return
        try:
            if self.search_type.get() == "lineal":
                self.resultado_busqueda = busqueda_lineal(self.datos, valor)
            else:
                if self.resultado_orden is None or not self.resultado_orden.arreglo:
                    messagebox.showwarning(
                        "Busqueda binaria",
                        "La busqueda binaria requiere datos ordenados. Ordene primero."
                    )
                    return
                self.resultado_busqueda = busqueda_binaria(self.resultado_orden.arreglo, valor)

            b = self.resultado_busqueda
            salida = (
                f"Busqueda completada\n"
                f"{'─'*46}\n"
                f"Valor    : {valor}\n"
                f"Metodo   : {self.search_type.get().capitalize()}\n"
                f"Resultado: {b.mensaje}\n"
            )
            if b.encontrado:
                salida += f"Ocurrencias: {len(b.indices)}\n"
                salida += f"Indices    : {b.indices[:50]}"
                if len(b.indices) > 50:
                    salida += f"  ... (+{len(b.indices)-50} mas)"
                salida += "\n"

            estado = "ok" if b.encontrado else "info"
            self._actualizar_estado(
                f"{'Valor encontrado' if b.encontrado else 'Valor no encontrado'}  |  {b.mensaje}", estado
            )
            self._mostrar_texto(salida)
        except Exception as error:
            messagebox.showerror("Error de busqueda", str(error))
            self._actualizar_estado("Error durante la busqueda.", "error")

    def _mostrar_resultados(self) -> None:
        if not self.datos:
            self._mostrar_texto("No hay datos cargados.\nUse el boton 'Cargar archivo'.")
            return

        r = self.resultado_orden
        b = self.resultado_busqueda

        salida = (
            f"Estado actual del sistema\n"
            f"{'─'*46}\n"
            f"Datos cargados    : {len(self.datos)} valores\n"
            f"Ordenamiento      : {r.algoritmo if r else 'Ninguno'}\n"
        )
        if r:
            salida += f"Tiempo orden.     : {r.tiempo_ms:.3f} ms\n"
            salida += f"Comparaciones     : {r.comparaciones}\n"
        salida += f"Ultima busqueda   : {b.valor if b else 'Ninguna'}\n"
        if b:
            salida += f"Resultado busq.   : {b.mensaje}\n"

        if r:
            salida += "\n" + self._obtener_vista_previa(r.arreglo)

        self._mostrar_texto(salida)
        self._actualizar_estado("Mostrando resumen del estado actual.", "info")

    def _exportar_resultados(self) -> None:
        if self.resultado_orden is None or not self.resultado_orden.arreglo:
            messagebox.showwarning("Exportar", "No hay resultados ordenados para exportar.")
            return
        ruta = filedialog.asksaveasfilename(
            title="Guardar resultados ordenados",
            defaultextension=".txt",
            filetypes=[
                ("Archivos TXT",  "*.txt"),
                ("Archivos XLSX", "*.xlsx"),
                ("Todos los archivos", "*.*"),
            ],
            initialfile=f"{ARCHIVO_POR_DEFECTO}.txt",
        )
        if not ruta:
            return
        try:
            exportar_resultados(
                self.resultado_orden.arreglo,
                ruta,
                self.resultado_orden.algoritmo,
                self.resultado_orden.tiempo_ms,
            )
            messagebox.showinfo("Exportacion", f"Resultados guardados en:\n{ruta}")
            self._actualizar_estado(f"Exportacion completada: {ruta.split('/')[-1]}", "ok")
        except Exception as error:
            messagebox.showerror("Error al exportar", str(error))
            self._actualizar_estado("Error durante la exportacion.", "error")

    def _mostrar_texto(self, texto: str) -> None:
        self._salida_text.configure(state="normal")
        self._salida_text.delete("1.0", tk.END)
        self._salida_text.insert(tk.END, texto)
        self._salida_text.configure(state="disabled")

    @staticmethod
    def _obtener_vista_previa(arreglo: List[float], limite: int = 20) -> str:
        total    = len(arreglo)
        primeros = "  ".join(str(v) for v in arreglo[:limite])
        ultimos  = "  ".join(str(v) for v in arreglo[-limite:]) if total else ""
        return (
            f"Total de registros: {total}\n\n"
            f"Primeros {min(limite, total)} valores:\n  [{primeros}]\n\n"
            f"Ultimos {min(limite, total)} valores:\n  [{ultimos}]\n"
        )


def run_app() -> None:
    app = DataApp()
    app.mainloop()
