# Sistema de Procesamiento y Ordenamiento Masivo de Datos

Proyecto escolar — 3er Semestre  
Materia: Estructura de Datos

Aplicación de escritorio desarrollada en Python con interfaz gráfica (Tkinter) para cargar, ordenar, buscar y exportar conjuntos de datos numéricos de gran tamaño, utilizando librerías propias de algoritmos de ordenamiento interno y externo.

---

## Características

- Carga de archivos **TXT** y **XLSX**
- **9 algoritmos de ordenamiento interno** (todos soportan orden ascendente y descendente)
- **5 algoritmos de ordenamiento externo** basados en mezcla de archivos temporales
- **Búsqueda secuencial** y **búsqueda binaria** con detección de duplicados
- Métricas en tiempo real: tiempo de ejecución, comparaciones, intercambios y complejidad
- Exportación de resultados a TXT o XLSX con metadatos del algoritmo
- Interfaz con vista previa de los primeros y últimos 20 valores

---

## Requisitos

- Python 3.10 o superior
- pandas
- openpyxl

Instalar dependencias:

```bash
pip install pandas openpyxl
```

---

## Ejecución

```bash
python main.py
```

> Ejecutar siempre desde la raíz del proyecto.

---

## Estructura del proyecto

```
├── main.py                          # Punto de entrada
├── libs/
│   ├── ordenamiento_interno.py      # 9 algoritmos internos + búsquedas
│   └── ordenamiento_externo.py      # 5 algoritmos externos con cintas temporales
├── gui/
│   └── app.py                       # Interfaz gráfica (Tkinter)
├── utils/
│   └── file_handler.py              # Lectura y escritura de TXT / XLSX
├── config/
│   └── settings.py                  # Constantes globales
└── Dataset examen/
    ├── dataset_1000_duplicados.txt
    └── dataset_5000_duplicados.xlsx
```

---

## Algoritmos implementados

### Ordenamiento Interno

Operan completamente en memoria RAM.

| Algoritmo      | Complejidad tiempo    | Complejidad espacio | Estable |
|----------------|-----------------------|---------------------|---------|
| Bubble Sort    | O(n²) / O(n) mejor   | O(1)                | Sí      |
| Selection Sort | O(n²)                 | O(1)                | No      |
| Insertion Sort | O(n²) / O(n) mejor   | O(1)                | Sí      |
| Shell Sort     | O(n log²n)            | O(1)                | No      |
| Merge Sort     | O(n log n)            | O(n)                | Sí      |
| Quick Sort     | O(n log n) / O(n²)   | O(log n)            | No      |
| Heap Sort      | O(n log n)            | O(1)                | No      |
| Counting Sort  | O(n + k)              | O(k)                | Sí      |
| Radix Sort     | O(nk)                 | O(n + k)            | Sí      |

### Ordenamiento Externo

Simulan procesamiento en disco mediante archivos temporales (cintas).

| Algoritmo                  | Descripción                                                  |
|----------------------------|--------------------------------------------------------------|
| Mezcla Directa             | Bloques de tamaño fijo, fusión 2-vías alternando cintas      |
| Mezcla Natural             | Detecta corridas naturales del archivo, menos pasadas        |
| Mezcla Equilibrada k-vías  | Fusión de k corridas simultáneas con heap mínimo             |
| Mezcla Polifásica          | Distribución Fibonacci, usa k−1 cintas de entrada            |
| Selección por Sustitución  | Genera corridas largas (~2×chunk) usando heap mínimo         |

### Búsquedas

| Método   | Requisito              | Devuelve                        |
|----------|------------------------|---------------------------------|
| Lineal   | Ninguno                | Todos los índices coincidentes  |
| Binaria  | Lista ordenada         | Todos los índices coincidentes  |

---

## Uso de la interfaz

1. **Cargar archivo** — selecciona un `.txt` o `.xlsx` con números enteros
2. **Seleccionar tipo** — Interno o Externo, Ascendente o Descendente
3. **Elegir algoritmo** — combobox con todos los métodos disponibles
4. **Ordenar datos** — ejecuta el algoritmo y muestra métricas en la consola
5. **Buscar valor** — ingresa un número y elige búsqueda Lineal o Binaria
6. **Mostrar resultados** — resumen del estado actual con primeros/últimos 20 valores
7. **Exportar** — guarda el arreglo ordenado junto con el algoritmo y tiempo usado

---

## Restricciones aplicadas

- No se usa `.sort()`, `sorted()` ni ninguna biblioteca automática de ordenamiento
- `pandas` y `openpyxl` se emplean únicamente para lectura y escritura de archivos
- Todos los algoritmos son implementaciones propias

---

## Comparación de rendimiento (dataset 5 000 registros)

| Escenario                    | Algoritmo recomendado       |
|------------------------------|-----------------------------|
| Datos pequeños               | Insertion Sort              |
| Datos masivos en memoria     | Quick Sort / Radix Sort     |
| Archivos externos (disco)    | Mezcla Natural / Sustitución|
| Datos parcialmente ordenados | Insertion Sort / Shell Sort |
| Búsquedas frecuentes         | Búsqueda Binaria            |
