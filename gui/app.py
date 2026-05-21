from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import List, Optional

from config.settings import ARCHIVO_POR_DEFECTO, MENSAJE_BIENVENIDA
from libs.busquedas import ResultadoBusqueda, busqueda_binaria, busqueda_lineal
from ordenamiento_interno import ResultadoOrden, ordenar_interno
from ordenamiento_externo import ordenar_externo
from utils.file_handler import cargar_datos, exportar_resultados


class DataApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Sistema de Procesamiento y Ordenamiento Masivo de Datos")
        self.geometry("920x640")
        self.resizable(False, False)

        self.datos: List[float] = []
        self.resultado_orden: Optional[ResultadoOrden] = None
        self.resultado_busqueda: Optional[ResultadoBusqueda] = None

        self.sort_type = tk.StringVar(value="interno")
        self.sort_method = tk.StringVar(value="bubble")
        self.sort_order = tk.StringVar(value="asc")
        self.search_type = tk.StringVar(value="lineal")
        self.chunk_size = tk.StringVar(value="100")
        self.search_value = tk.StringVar()

        self._crear_componentes()
        self._actualizar_estado("Listo para cargar datos.")

    def _crear_componentes(self) -> None:
        boton_frame = ttk.Frame(self, padding=12)
        boton_frame.grid(row=0, column=0, sticky="ew")

        ttk.Button(boton_frame, text="Cargar archivo", command=self._cargar_archivo).grid(
            row=0, column=0, padx=4, pady=4, sticky="ew"
        )
        ttk.Button(boton_frame, text="Exportar resultados", command=self._exportar_resultados).grid(
            row=0, column=1, padx=4, pady=4, sticky="ew"
        )
        ttk.Button(boton_frame, text="Mostrar resultados", command=self._mostrar_resultados).grid(
            row=0, column=2, padx=4, pady=4, sticky="ew"
        )
        ttk.Button(boton_frame, text="Salir", command=self.quit).grid(
            row=0, column=3, padx=4, pady=4, sticky="ew"
        )

        boton_frame.columnconfigure((0, 1, 2, 3), weight=1)

        orden_frame = ttk.LabelFrame(self, text="Ordenamiento", padding=12)
        orden_frame.grid(row=1, column=0, padx=12, pady=8, sticky="ew")

        ttk.Radiobutton(
            orden_frame,
            text="Interno",
            variable=self.sort_type,
            value="interno",
            command=self._actualizar_opciones_ordenamiento,
        ).grid(row=0, column=0, padx=4, pady=4, sticky="w")
        ttk.Radiobutton(
            orden_frame,
            text="Externo",
            variable=self.sort_type,
            value="externo",
            command=self._actualizar_opciones_ordenamiento,
        ).grid(row=0, column=1, padx=4, pady=4, sticky="w")
        ttk.Radiobutton(
            orden_frame,
            text="Ascendente",
            variable=self.sort_order,
            value="asc",
        ).grid(row=0, column=2, padx=4, pady=4, sticky="w")
        ttk.Radiobutton(
            orden_frame,
            text="Descendente",
            variable=self.sort_order,
            value="desc",
        ).grid(row=0, column=3, padx=4, pady=4, sticky="w")

        ttk.Label(orden_frame, text="Método interno:").grid(row=1, column=0, padx=4, pady=6, sticky="w")
        self._metodo_combo = ttk.Combobox(
            orden_frame,
            textvariable=self.sort_method,
            values=["bubble", "insertion", "merge"],
            state="readonly",
        )
        self._metodo_combo.grid(row=1, column=1, padx=4, pady=6, sticky="ew")

        ttk.Label(orden_frame, text="Chunk size (externo):").grid(row=2, column=0, padx=4, pady=6, sticky="w")
        self._chunk_entry = ttk.Entry(orden_frame, textvariable=self.chunk_size, width=12)
        self._chunk_entry.grid(row=2, column=1, padx=4, pady=6, sticky="w")

        ttk.Button(orden_frame, text="Ordenar", command=self._ordenar_datos).grid(
            row=3, column=0, columnspan=2, padx=4, pady=8, sticky="ew"
        )

        orden_frame.columnconfigure(1, weight=1)

        busqueda_frame = ttk.LabelFrame(self, text="Búsqueda", padding=12)
        busqueda_frame.grid(row=2, column=0, padx=12, pady=8, sticky="ew")

        ttk.Label(busqueda_frame, text="Valor a buscar:").grid(row=0, column=0, padx=4, pady=4, sticky="w")
        ttk.Entry(busqueda_frame, textvariable=self.search_value, width=24).grid(
            row=0, column=1, padx=4, pady=4, sticky="w"
        )

        ttk.Radiobutton(
            busqueda_frame,
            text="Lineal",
            variable=self.search_type,
            value="lineal",
        ).grid(row=1, column=0, padx=4, pady=4, sticky="w")
        ttk.Radiobutton(
            busqueda_frame,
            text="Binaria",
            variable=self.search_type,
            value="binaria",
        ).grid(row=1, column=1, padx=4, pady=4, sticky="w")

        ttk.Button(busqueda_frame, text="Buscar", command=self._buscar_valor).grid(
            row=2, column=0, columnspan=2, padx=4, pady=8, sticky="ew"
        )

        salida_frame = ttk.LabelFrame(self, text="Salida", padding=12)
        salida_frame.grid(row=3, column=0, padx=12, pady=8, sticky="nsew")

        self._salida_text = tk.Text(salida_frame, height=18, wrap="word", state="disabled")
        self._salida_text.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(salida_frame, command=self._salida_text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self._salida_text.configure(yscrollcommand=scrollbar.set)

        salida_frame.columnconfigure(0, weight=1)
        salida_frame.rowconfigure(0, weight=1)

        self._estado_label = ttk.Label(self, text="", anchor="w")
        self._estado_label.grid(row=4, column=0, padx=12, pady=(0, 12), sticky="ew")

        self.columnconfigure(0, weight=1)

        self._actualizar_opciones_ordenamiento()

    def _actualizar_estado(self, mensaje: str) -> None:
        self._estado_label.config(text=mensaje)

    def _actualizar_opciones_ordenamiento(self) -> None:
        modo = self.sort_type.get()
        if modo == "interno":
            self._metodo_combo.configure(state="readonly")
            self._chunk_entry.configure(state="disabled")
        else:
            self._metodo_combo.configure(state="disabled")
            self._chunk_entry.configure(state="normal")

    def _cargar_archivo(self) -> None:
        ruta = filedialog.askopenfilename(
            title="Seleccionar archivo de datos",
            filetypes=[("Archivos TXT", "*.txt"), ("Archivos XLSX", "*.xlsx"), ("Todos los archivos", "*")],
        )
        if not ruta:
            return

        try:
            self.datos = cargar_datos(ruta)
            self.resultado_orden = None
            self.resultado_busqueda = None
            self._actualizar_estado(f"Archivo cargado: {ruta} ({len(self.datos)} valores)")
            self._mostrar_texto(f"Datos cargados desde:\n{ruta}\nTotal de valores: {len(self.datos)}\n")
        except Exception as error:
            messagebox.showerror("Error al cargar archivo", str(error))
            self._actualizar_estado("Fallo al cargar el archivo.")

    def _ordenar_datos(self) -> None:
        if not self.datos:
            messagebox.showwarning("Ordenamiento", "Debe cargar un archivo antes de ordenar.")
            return

        try:
            reversa = self.sort_order.get() == "desc"
            if self.sort_type.get() == "interno":
                metodo = self.sort_method.get()
                self.resultado_orden = ordenar_interno(
                    self.datos,
                    metodo=metodo,
                    reversa=reversa,
                )
            else:
                chunk_value = self.chunk_size.get().strip()
                if not chunk_value.isdigit() or int(chunk_value) < 1:
                    raise ValueError("El tamaño de chunk debe ser un entero positivo.")
                self.resultado_orden = ordenar_externo(
                    self.datos,
                    chunk_size=int(chunk_value),
                    reversa=reversa,
                )

            detalles = (
                f"Ordenamiento finalizado:\nAlgoritmo: {self.resultado_orden.algoritmo}\n"
                f"Orden: {'Descendente' if reversa else 'Ascendente'}\n"
                f"Tiempo: {self.resultado_orden.tiempo_ms:.2f} ms\n"
                f"Cantidad de valores: {len(self.resultado_orden.arreglo)}\n"
            )
            self._actualizar_estado("Ordenamiento completado.")
            self._mostrar_texto(detalles + self._obtener_vista_previa(self.resultado_orden.arreglo))
        except Exception as error:
            messagebox.showerror("Error de ordenamiento", str(error))
            self._actualizar_estado("Fallo en el ordenamiento.")

    def _buscar_valor(self) -> None:
        if not self.datos:
            messagebox.showwarning("Búsqueda", "Debe cargar un archivo antes de buscar.")
            return

        valor_texto = self.search_value.get().strip()
        if not valor_texto:
            messagebox.showwarning("Búsqueda", "Ingrese un valor a buscar.")
            return

        try:
            valor = float(valor_texto)
        except ValueError:
            messagebox.showerror("Búsqueda", "Ingrese un número válido.")
            return

        try:
            if self.search_type.get() == "lineal":
                self.resultado_busqueda = busqueda_lineal(self.datos, valor)
            else:
                if self.resultado_orden is None or not self.resultado_orden.arreglo:
                    messagebox.showwarning(
                        "Búsqueda binaria",
                        "La búsqueda binaria requiere datos ordenados. Ordene primero."
                    )
                    return
                self.resultado_busqueda = busqueda_binaria(self.resultado_orden.arreglo, valor)

            texto = (
                f"Búsqueda de valor: {valor}\n"
                f"Método: {self.search_type.get().capitalize()}\n"
                f"Resultado: {self.resultado_busqueda.mensaje}\n"
            )
            if self.resultado_busqueda.encontrado:
                texto += f"Índice(s): {self.resultado_busqueda.indices}\n"
            self._actualizar_estado("Búsqueda completada.")
            self._mostrar_texto(texto)
        except Exception as error:
            messagebox.showerror("Error de búsqueda", str(error))
            self._actualizar_estado("Fallo en la búsqueda.")

    def _mostrar_resultados(self) -> None:
        if not self.datos:
            self._mostrar_texto("No hay datos cargados. Use el botón 'Cargar archivo'.")
            return

        resumen = [
            f"Datos cargados: {len(self.datos)} valores",
            f"Ordenamiento activo: {self.resultado_orden.algoritmo if self.resultado_orden else 'Ninguno'}",
            f"Búsqueda activa: {self.resultado_busqueda.valor if self.resultado_busqueda else 'Ninguna'}",
        ]

        if self.resultado_orden:
            resumen.append(f"Tiempo de ordenamiento: {self.resultado_orden.tiempo_ms:.2f} ms")
            resumen.append(self._obtener_vista_previa(self.resultado_orden.arreglo))

        if self.resultado_busqueda:
            resumen.append(f"Último resultado de búsqueda: {self.resultado_busqueda.mensaje}")
            if self.resultado_busqueda.encontrado:
                resumen.append(f"Índice(s): {self.resultado_busqueda.indices}")

        self._mostrar_texto("\n".join(resumen))
        self._actualizar_estado("Mostrando el estado actual.")

    def _exportar_resultados(self) -> None:
        if self.resultado_orden is None or not self.resultado_orden.arreglo:
            messagebox.showwarning("Exportar", "No hay resultados ordenados para exportar.")
            return

        ruta = filedialog.asksaveasfilename(
            title="Guardar resultados ordenados",
            defaultextension=".txt",
            filetypes=[("Archivos TXT", "*.txt"), ("Archivos XLSX", "*.xlsx")],
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
            messagebox.showinfo("Exportación", f"Resultados guardados en:\n{ruta}")
            self._actualizar_estado("Exportación completada.")
        except Exception as error:
            messagebox.showerror("Error al exportar", str(error))
            self._actualizar_estado("Fallo en la exportación.")

    def _mostrar_texto(self, texto: str) -> None:
        self._salida_text.configure(state="normal")
        self._salida_text.delete("1.0", tk.END)
        self._salida_text.insert(tk.END, texto)
        self._salida_text.configure(state="disabled")

    @staticmethod
    def _obtener_vista_previa(arreglo: List[float], limite: int = 20) -> str:
        total = len(arreglo)
        primeros = ", ".join(str(valor) for valor in arreglo[:limite])
        ultimos = ", ".join(str(valor) for valor in arreglo[-limite:]) if total else ""
        return (
            f"Total de registros: {total}\n"
            f"Primeros {min(limite, total)} valores:\n[{primeros}]\n"
            f"Últimos {min(limite, total)} valores:\n[{ultimos}]\n"
        )


def run_app() -> None:
    app = DataApp()
    app.mainloop()
