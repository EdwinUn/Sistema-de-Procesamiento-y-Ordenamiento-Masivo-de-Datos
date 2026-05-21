#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd

# Importación de las librerías propias proporcionadas por el alumno
try:
    import metodos_internos as internal
    import metodos_externos as external
except ImportError:
    messagebox.showerror(
        "Error de Importación", 
        "Asegúrate de que 'internal_sorting.py' y 'external_sorting.py' "
        "estén en la misma carpeta que este script."
    )


# ══════════════════════════════════════════════════════════════════════════
#  MÉTODOS DE BÚSQUEDA CON MÉTRICAS
# ══════════════════════════════════════════════════════════════════════════

def busqueda_secuencial(arr, target):
    """Busca un valor de forma secuencial y calcula comparaciones y tiempo."""
    inicio = time.perf_counter()
    comparaciones = 0
    posiciones = []
    
    for i in range(len(arr)):
        comparaciones += 1
        if arr[i] == target:
            posiciones.append(i)
            
    tiempo_ms = (time.perf_counter() - inicio) * 1000
    return posiciones, comparaciones, tiempo_ms


def busqueda_binaria(arr, target, es_ascendente=True):
    """
    Busca un valor usando búsqueda binaria. 
    Detecta si el arreglo está invertido (descendente) para ajustar la lógica.
    """
    inicio = time.perf_counter()
    comparaciones = 0
    low = 0
    high = len(arr) - 1
    posiciones = []

    while low <= high:
        comparaciones += 1
        mid = (low + high) // 2
        if arr[mid] == target:
            # Encontrar ocurrencias adyacentes si existen duplicados
            posiciones.append(mid)
            # Buscar a la izquierda
            i = mid - 1
            while i >= 0 and arr[i] == target:
                posiciones.append(i)
                i -= 1
            # Buscar a la derecha
            i = mid + 1
            while i < len(arr) and arr[i] == target:
                posiciones.append(i)
                i += 1
            break
        
        if es_ascendente:
            if arr[mid] < target:
                low = mid + 1
            else:
                high = mid - 1
        else:  # Caso descendente
            if arr[mid] > target:
                low = mid + 1
            else:
                high = mid - 1

    tiempo_ms = (time.perf_counter() - inicio) * 1000
    return sorted(posiciones), comparaciones, tiempo_ms


class EstructuraHash:
    """Simulación de Tabla Hash con encadenamiento para búsquedas O(1)."""
    def __init__(self, size):
        self.size = size
        self.tabla = [[] for _ in range(size)]
        
    def _hash(self, clave):
        return abs(hash(clave)) % self.size
        
    def insertar(self, clave, indice_original):
        idx = self._hash(clave)
        self.tabla[idx].append((clave, indice_original))
        
    def buscar(self, clave):
        inicio = time.perf_counter()
        idx = self._hash(clave)
        comparaciones = 0
        resultados = []
        
        for c, idx_orig in self.tabla[idx]:
            comparaciones += 1
            if c == clave:
                resultados.append(idx_orig)
                
        tiempo_ms = (time.perf_counter() - inicio) * 1000
        return resultados, comparaciones, tiempo_ms


# ══════════════════════════════════════════════════════════════════════════
#  INTERFAZ GRÁFICA (TKINTER)
# ══════════════════════════════════════════════════════════════════════════

class AppSistemaProcesamiento:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Procesamiento y Ordenamiento Masivo de Datos")
        self.root.geometry("900x700")
        self.root.minsize(850, 650)
        
        # Variables de estado de datos
        self.datos_originales = []
        self.datos_procesados = []
        self.ultimo_resultado_metricas = {}
        self.hash_tabla = None
        self.es_ascendente = True

        self._crear_estilos()
        self._construir_interfaz()

    def _crear_estilos(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TFrame", background="#f5f5f5")
        self.style.configure("TLabelframe", background="#f5f5f5", foreground="#333333")
        self.style.configure("TLabelframe.Label", font=("Helvetica", 10, "bold"), background="#f5f5f5")
        self.style.configure("TButton", font=("Helvetica", 9, "bold"), padding=5)
        self.style.configure("Header.TLabel", font=("Helvetica", 14, "bold"), background="#f5f5f5", foreground="#1a365d")

    def _construir_interfaz(self):
        # Contenedor Principal
        main_frame = ttk.Frame(self.root, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Título
        lbl_titulo = ttk.Label(main_frame, text="Sistema de Procesamiento y Ordenamiento Masivo", style="Header.TLabel")
        lbl_titulo.pack(anchor=tk.W, pady=(0, 15))

        # ── SECCIÓN 1: CARGA DE ARCHIVO ──
        frame_carga = ttk.LabelFrame(main_frame, text=" 1. Lectura de Archivos (TXT / XLSX) ", padding=10)
        frame_carga.pack(fill=tk.X, pady=(0, 10))

        self.btn_cargar = ttk.Button(frame_carga, text="Seleccionar Archivo", command=self._cargar_archivo)
        self.btn_cargar.pack(side=tk.LEFT, padx=(0, 10))

        self.lbl_info_archivo = ttk.Label(frame_carga, text="Ningún archivo cargado.", font=("Helvetica", 9, "italic"), background="#f5f5f5")
        self.lbl_info_archivo.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # ── SECCIÓN 2: CONFIGURACIÓN DE ORDENAMIENTO ──
        frame_orden = ttk.LabelFrame(main_frame, text=" 2. Algoritmos de Ordenamiento ", padding=10)
        frame_orden.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(frame_orden, text="Tipo:", background="#f5f5f5").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.cmb_tipo_orden = ttk.Combobox(frame_orden, values=["Interno (RAM)", "Externo (Disco)"], state="readonly", width=18)
        self.cmb_tipo_orden.grid(row=0, column=1, padx=5, pady=5)
        self.cmb_tipo_orden.bind("<<ComboboxSelected>>", self._actualizar_algoritmos)

        ttk.Label(frame_orden, text="Algoritmo:", background="#f5f5f5").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.cmb_algoritmo = ttk.Combobox(frame_orden, state="readonly", width=25)
        self.cmb_algoritmo.grid(row=0, column=3, padx=5, pady=5)

        # Dirección del ordenamiento
        self.var_direccion = tk.StringVar(value="ASC")
        rad_asc = ttk.Radiobutton(frame_orden, text="Ascendente", variable=self.var_direccion, value="ASC")
        rad_desc = ttk.Radiobutton(frame_orden, text="Descendente", variable=self.var_direccion, value="DESC")
        rad_asc.grid(row=0, column=4, padx=10, pady=5)
        rad_desc.grid(row=0, column=5, padx=10, pady=5)

        self.btn_ordenar = ttk.Button(frame_orden, text="Ejecutar Ordenamiento", command=self._ejecutar_ordenamiento)
        self.btn_ordenar.grid(row=0, column=6, padx=15, pady=5)

        # ── SECCIÓN 3: VISUALIZACIÓN DE RESULTADOS Y MÉTRICAS ──
        frame_resultados = ttk.LabelFrame(main_frame, text=" 3. Monitoreo y Resultados ", padding=10)
        frame_resultados.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Subframe izquierdo: Muestras de datos
        sub_datos = ttk.Frame(frame_resultados)
        sub_datos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        ttk.Label(sub_datos, text="Primeros 20 elementos:", font=("Helvetica", 9, "bold"), background="#f5f5f5").pack(anchor=tk.W)
        self.txt_primeros = tk.Text(sub_datos, height=4, wrap=tk.WORD, font=("Consolas", 9))
        self.txt_primeros.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(sub_datos, text="Últimos 20 elementos:", font=("Helvetica", 9, "bold"), background="#f5f5f5").pack(anchor=tk.W)
        self.txt_ultimos = tk.Text(sub_datos, height=4, wrap=tk.WORD, font=("Consolas", 9))
        self.txt_ultimos.pack(fill=tk.X, pady=(0, 5))

        # Subframe derecho: Métricas en formato de texto
        sub_metricas = ttk.Frame(frame_resultados, width=320)
        sub_metricas.pack_propagate(False)
        sub_metricas.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(5, 0))

        self.txt_metricas = tk.Text(sub_metricas, wrap=tk.WORD, font=("Consolas", 9), background="#edf2f7")
        self.txt_metricas.pack(fill=tk.BOTH, expand=True)

        # ── SECCIÓN 4: BÚSQUEDA DE VALORES ──
        frame_busqueda = ttk.LabelFrame(main_frame, text=" 4. Métodos de Búsqueda ", padding=10)
        frame_busqueda.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(frame_busqueda, text="Valor a buscar:", background="#f5f5f5").grid(row=0, column=0, padx=5, pady=5)
        self.ent_target = ttk.Entry(frame_busqueda, width=12)
        self.ent_target.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame_busqueda, text="Método:", background="#f5f5f5").grid(row=0, column=2, padx=5, pady=5)
        self.cmb_metodo_busqueda = ttk.Combobox(frame_busqueda, values=["Secuencial", "Binaria", "Hash"], state="readonly", width=15)
        self.cmb_metodo_busqueda.grid(row=0, column=3, padx=5, pady=5)
        self.cmb_metodo_busqueda.current(0)

        self.btn_buscar = ttk.Button(frame_busqueda, text="Buscar Valor", command=self._ejecutar_busqueda)
        self.btn_buscar.grid(row=0, column=4, padx=15, pady=5)

        self.lbl_resultado_busqueda = ttk.Label(frame_busqueda, text="Resultado de búsqueda: -", font=("Helvetica", 9, "bold"), foreground="#2b6cb0", background="#f5f5f5")
        self.lbl_resultado_busqueda.grid(row=0, column=5, columnspan=2, sticky=tk.W, padx=10, pady=5)

        # ── SECCIÓN 5: EXPORTACIÓN ──
        frame_export = ttk.Frame(main_frame)
        frame_export.pack(fill=tk.X)

        self.btn_exportar = ttk.Button(frame_export, text="Exportar Resultados Auditados", command=self._exportar_resultados, state=tk.DISABLED)
        self.btn_exportar.pack(side=tk.RIGHT)

        # Inicialización de Combobox de Ordenamientos
        self.cmb_tipo_orden.current(0)
        self._actualizar_algoritmos(None)

    # ══════════════════════════════════════════════════════════════════════════
    #  LÓGICA OPERACIONAL CONTROLLER
    # ══════════════════════════════════════════════════════════════════════════

    def _actualizar_algoritmos(self, event):
        """Modifica dinámicamente el catálogo de algoritmos según el entorno de ejecución."""
        if self.cmb_tipo_orden.get() == "Interno (RAM)":
            algoritmos = [
                "Bubble Sort", "Selection Sort", "Insertion Sort", "Shell Sort",
                "Merge Sort", "Quick Sort", "Heap Sort", "Counting Sort", "Radix Sort"
            ]
        else:
            algoritmos = ["Mezcla Directa", "Mezcla Natural", "Mezcla Equilibrada"]
        
        self.cmb_algoritmo.config(values=algoritmos)
        self.cmb_algoritmo.current(0)

    def _cargar_archivo(self):
        """Lee y valida archivos planos o estructuras tabulares numéricas."""
        ruta = filedialog.askopenfilename(
            title="Abrir set numérico de datos",
            filetypes=[("Archivos admitidos", "*.txt *.xlsx"), ("Texto plano", "*.txt"), ("Excel", "*.xlsx")]
        )
        if not ruta:
            return

        try:
            valores = []
            if ruta.endswith(".txt"):
                with open(ruta, "r") as f:
                    for linea in f:
                        linea = linea.strip()
                        if linea:
                            valores.append(int(linea))
            elif ruta.endswith(".xlsx"):
                df = pd.read_excel(ruta, header=None)
                valores = df.iloc[:, 0].dropna().astype(int).tolist()

            self.datos_originales = valores
            self.datos_procesados = valores[:]  
            self.hash_tabla = None 

            self.lbl_info_archivo.config(
                text=f"Archivo: {os.path.basename(ruta)} | Total registros: {len(self.datos_originales)}"
            )
            self._renderizar_muestras_datos()
            self.btn_exportar.config(state=tk.DISABLED)
            messagebox.showinfo("Carga Completada", f"Se han cargado {len(self.datos_originales)} elementos correctamente.")

        except Exception as e:
            messagebox.showerror("Error de Procesamiento", f"No se pudo estructurar el archivo:\n{str(e)}")

    def _renderizar_muestras_datos(self):
        """Muestra de manera dinámica los primeros y últimos 20 registros solicitados."""
        self.txt_primeros.delete("1.0", tk.END)
        self.txt_ultimos.delete("1.0", tk.END)

        if not self.datos_procesados:
            return

        primeros = self.datos_procesados[:20]
        ultimos = self.datos_procesados[-20:]

        self.txt_primeros.insert(tk.END, ", ".join(map(str, primeros)))
        self.txt_ultimos.insert(tk.END, ", ".join(map(str, ultimos)))

    def _ejecutar_ordenamiento(self):
        """Consume los algoritmos de las librerías propias inyectando la información."""
        if not self.datos_originales:
            messagebox.showwarning("Sin Origen de Datos", "Por favor, cargue un archivo primero.")
            return

        tipo = self.cmb_tipo_orden.get()
        algoritmo = self.cmb_algoritmo.get()
        self.es_ascendente = (self.var_direccion.get() == "ASC")

        datos_trabajo = self.datos_originales[:]
        self.hash_tabla = None 

        try:
            if tipo == "Interno (RAM)":
                dic_internos = {
                    "Bubble Sort": internal.bubble_sort,
                    "Selection Sort": internal.selection_sort,
                    "Insertion Sort": internal.insertion_sort,
                    "Shell Sort": internal.shell_sort,
                    "Merge Sort": internal.merge_sort,
                    "Quick Sort": internal.quick_sort,
                    "Heap Sort": internal.heap_sort,
                    "Counting Sort": internal.counting_sort,
                    "Radix Sort": internal.radix_sort
                }
                
                res = dic_internos[algoritmo](datos_trabajo)
                
                if not self.es_ascendente:
                    res.arreglo = res.arreglo[::-1]

                self.datos_procesados = res.arreglo
                
                self.ultimo_resultado_metricas = {
                    "Algoritmo": res.algoritmo,
                    "Tiempo": f"{res.tiempo_ms:.4f} ms",
                    "Comparaciones": res.comparaciones,
                    "Intercambios": res.interchanges if hasattr(res, 'interchanges') else res.intercambios,
                    "Complejidad T": res.complejidad_t,
                    "Complejidad E": res.complejidad_e
                }

            else:
                if algoritmo == "Mezcla Directa":
                    res = external.mezcla_directa(datos_trabajo)
                elif algoritmo == "Mezcla Natural":
                    res = external.mezcla_natural(datos_trabajo)
                else:
                    res = external.mezcla_equilibrada(datos_trabajo)

                if not self.es_ascendente:
                    res.arreglo = res.arreglo[::-1]

                self.datos_procesados = res.arreglo

                self.ultimo_resultado_metricas = {
                    "Algoritmo": res.algoritmo,
                    "Tiempo": f"{res.tiempo_ms:.4f} ms",
                    "Comparaciones": res.comparaciones,
                    "Pasadas Disco": res.pasadas,
                    "Lecturas I/O": res.lecturas,
                    "Escrituras I/O": res.escrituras,
                    "Bloque Inicial": f"{res.chunk_size} items"
                }

            self._renderizar_muestras_datos()
            self._mostrar_metricas_texto()
            self.btn_exportar.config(state=tk.NORMAL)

        except Exception as e:
            messagebox.showerror("Fallo de Algoritmo", f"Ocurrió una anomalía durante el ordenamiento:\n{str(e)}")

    def _mostrar_metricas_texto(self):
        """Imprime de manera legible los metadatos de rendimiento del algoritmo."""
        self.txt_metricas.delete("1.0", tk.END)
        self.txt_metricas.insert(tk.END, f" EJECUCIÓN EXITOSA\n")
        self.txt_metricas.insert(tk.END, f" ═════════════════════════\n")
        self.txt_metricas.insert(tk.END, f" Total registros: {len(self.datos_procesados)}\n")
        
        for k, v in self.ultimo_resultado_metricas.items():
            self.txt_metricas.insert(tk.END, f" {k}: {v}\n")

    def _ejecutar_busqueda(self):
        """Orquesta la estrategia de búsqueda solicitada sobre el set de datos procesado."""
        if not self.datos_procesados:
            messagebox.showwarning("Sin Datos", "Debe ordenar o cargar datos antes de buscar.")
            return

        try:
            target = int(self.ent_target.get().strip())
        except ValueError:
            messagebox.showerror("Error de Entrada", "El valor a buscar debe ser un número entero válido.")
            return

        metodo = self.cmb_metodo_busqueda.get()

        if metodo == "Secuencial":
            indices, comp, tiempo = busqueda_secuencial(self.datos_procesados, target)
            
        elif metodo == "Binaria":
            indices, comp, tiempo = busqueda_binaria(self.datos_procesados, target, es_ascendente=self.es_ascendente)
            
        elif metodo == "Hash":
            if self.hash_tabla is None:
                self.hash_tabla = EstructuraHash(size=len(self.datos_procesados) * 2)
                for i, val in enumerate(self.datos_procesados):
                    self.hash_tabla.insert(val, i)
                    
            indices, comp, tiempo = self.hash_tabla.buscar(target)

        if indices:
            res_text = f"Encontrado en índice(s): {indices}\n[Comparaciones: {comp} | Tiempo: {tiempo:.4f} ms]"
        else:
            res_text = f"Valor no localizado en el set.\n[Comparaciones: {comp} | Tiempo: {tiempo:.4f} ms]"
            
        self.lbl_resultado_busqueda.config(text=f"Resultado: {res_text}")

    def _exportar_resultados(self):
        """Almacena la información procesada junto a su auditoría técnica en disco."""
        if not self.datos_procesados:
            return

        ruta_salida = filedialog.asksaveasfilename(
            title="Guardar resultados ordenados",
            defaultextension=".txt",
            filetypes=[("Texto Plano", "*.txt"), ("Libro de Excel", "*.xlsx")]
        )
        if not ruta_salida:
            return

        try:
            if ruta_salida.endswith(".txt"):
                with open(ruta_salida, "w", encoding="utf-8") as f:
                    f.write("════════════════════════════════════════════════════════\n")
                    f.write("          REPORTE DE AUDITORÍA DE PROCESAMIENTO\n")
                    f.write("════════════════════════════════════════════════════════\n")
                    f.write(f" Algoritmo Utilizado: {self.ultimo_resultado_metricas.get('Algoritmo', 'N/A')}\n")
                    f.write(f" Sentido del orden: {'Ascendente' if self.es_ascendente else 'Descendente'}\n")
                    f.write(f" Tiempo transcurrido: {self.ultimo_resultado_metricas.get('Tiempo', 'N/A')}\n")
                    f.write(f" Total de registros exportados: {len(self.datos_procesados)}\n")
                    f.write("════════════════════════════════════════════════════════\n\n")
                    f.write("REGISTROS ORDENADOS:\n")
                    for item in self.datos_procesados:
                        f.write(f"{item}\n")
                        
            elif ruta_salida.endswith(".xlsx"):
                df_datos = pd.DataFrame(self.datos_procesados, columns=["Valores Ordenados"])
                
                meta_datos = []
                for k, v in self.ultimo_resultado_metricas.items():
                    meta_datos.append([k, str(v)])
                df_meta = pd.DataFrame(meta_datos, columns=["Métrica", "Valor"])
                
                with pd.ExcelWriter(ruta_salida, engine='openpyxl') as writer:
                    df_datos.to_excel(writer, sheet_name="Datos Ordenados", index=False)
                    df_meta.to_excel(writer, sheet_name="Auditoría de Execution", index=False)

            messagebox.showinfo("Exportación Completada", f"Archivo salvado de forma íntegra en:\n{ruta_salida}")

        except Exception as e:
            messagebox.showerror("Error al Guardar", f"No se pudo guardar el archivo final:\n{str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = AppSistemaProcesamiento(root)
    root.mainloop()