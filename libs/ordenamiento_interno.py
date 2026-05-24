"""
╔══════════════════════════════════════════════════════════════════════════╗
║          LIBRERÍA DE ORDENAMIENTO INTERNO  — internal_sorting.py         ║
║  Algoritmos que operan completamente en memoria RAM.                     ║
║                                                                          ║
║  Métodos incluidos:                                                      ║
║    1. Bubble Sort       — O(n²)      estable,   in-place                 ║
║    2. Selection Sort    — O(n²)      inestable, in-place                 ║
║    3. Insertion Sort    — O(n²)/O(n) estable,   in-place                 ║
║    4. Shell Sort        — O(n log²n) inestable, in-place                 ║
║    5. Merge Sort        — O(n log n) estable,   O(n) espacio             ║
║    6. Quick Sort        — O(n log n) inestable, in-place                 ║
║    7. Heap Sort         — O(n log n) inestable, in-place                 ║
║    8. Counting Sort     — O(n + k)   estable,   O(k) espacio             ║
║    9. Radix Sort        — O(nk)      estable,   O(n + k) espacio         ║
╚══════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
import time


# ══════════════════════════════════════════════════════════════════════════
#  RESULTADO ESTÁNDAR
# ══════════════════════════════════════════════════════════════════════════

@dataclass
class ResultadoOrden:
    """Encapsula el arreglo ordenado y las métricas de rendimiento."""
    arreglo:        List[int]
    comparaciones:  int = 0
    intercambios:   int = 0
    tiempo_ms:      float = 0.0
    algoritmo:      str = ""
    complejidad_t:  str = ""
    complejidad_e:  str = ""
    detalles:       str = ""

    def __str__(self) -> str:
        sep = "─" * 46
        return (
            f"\n{sep}\n"
            f"  Algoritmo : {self.algoritmo}\n"
            f"  Arreglo   : {self.arreglo}\n"
            f"  Compar.   : {self.comparaciones}\n"
            f"  Intercamb.: {self.intercambios}\n"
            f"  Tiempo    : {self.tiempo_ms:.4f} ms\n"
            f"  Complejidad Tiempo  : {self.complejidad_t}\n"
            f"  Complejidad Espacio : {self.complejidad_e}\n"
            f"{sep}"
        )


METODOS_INTERNOS = (
    "bubble", "selection", "insertion", "shell",
    "merge", "quick", "heap", "counting", "radix",
)


def ordenar_interno(arr: List[int], metodo: str = "bubble", reversa: bool = False) -> ResultadoOrden:
    if metodo == "bubble":
        return bubble_sort(arr, reversa=reversa)
    if metodo == "selection":
        return selection_sort(arr, reversa=reversa)
    if metodo == "insertion":
        return insertion_sort(arr, reversa=reversa)
    if metodo == "shell":
        return shell_sort(arr, reversa=reversa)
    if metodo == "merge":
        return merge_sort(arr, reversa=reversa)
    if metodo == "quick":
        return quick_sort(arr, reversa=reversa)
    if metodo == "heap":
        return heap_sort(arr, reversa=reversa)
    if metodo == "counting":
        return counting_sort(arr, reversa=reversa)
    if metodo == "radix":
        return radix_sort(arr, reversa=reversa)
    raise ValueError(f"Método de ordenamiento interno desconocido: {metodo}")


# ══════════════════════════════════════════════════════════════════════════
#  DECORADOR DE TIEMPO
# ══════════════════════════════════════════════════════════════════════════

def _medir(func):
    """Mide el tiempo de ejecución y lo inyecta en el ResultadoOrden."""
    def wrapper(arr: List[int], *args, **kwargs) -> ResultadoOrden:
        inicio = time.perf_counter()
        resultado = func(arr[:], *args, **kwargs)   # copia defensiva
        resultado.tiempo_ms = (time.perf_counter() - inicio) * 1000
        return resultado
    wrapper.__name__ = func.__name__
    wrapper.__doc__  = func.__doc__
    return wrapper


# ══════════════════════════════════════════════════════════════════════════
#  1. BUBBLE SORT
# ══════════════════════════════════════════════════════════════════════════

@_medir
def bubble_sort(arr: List[int], reversa: bool = False) -> ResultadoOrden:
    """
    Burbuja: recorre el arreglo comparando pares adyacentes e intercambiando
    si están en el orden incorrecto. En cada pasada el elemento máximo
    'burbujea' hasta el final.

    Mejor caso  : O(n)   — lista ya ordenada (con flag de intercambio)
    Peor / Med. : O(n²)
    Espacio     : O(1)   in-place, estable
    """
    n   = len(arr)
    cmp = intercambios = 0

    for i in range(n - 1):
        hubo_intercambio = False
        for j in range(0, n - i - 1):
            cmp += 1
            if (not reversa and arr[j] > arr[j + 1]) or (reversa and arr[j] < arr[j + 1]):
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                intercambios += 1
                hubo_intercambio = True
        if not hubo_intercambio:   # optimización: lista ya ordenada
            break

    return ResultadoOrden(
        arreglo=arr, comparaciones=cmp, intercambios=intercambios,
        algoritmo="Bubble Sort Descendente" if reversa else "Bubble Sort",
        complejidad_t="O(n²) — O(n) mejor caso",
        complejidad_e="O(1)"
    )


# ══════════════════════════════════════════════════════════════════════════
#  2. SELECTION SORT
# ══════════════════════════════════════════════════════════════════════════

@_medir
def selection_sort(arr: List[int], reversa: bool = False) -> ResultadoOrden:
    """
    Selección: en cada pasada busca el elemento extremo (mínimo o máximo)
    en la parte no ordenada y lo coloca al inicio de dicha parte.

    Complejidad : O(n²) en todos los casos
    Espacio     : O(1)  in-place, inestable
    Ventaja     : mínimo de intercambios (exactamente n-1)
    """
    n   = len(arr)
    cmp = intercambios = 0

    for i in range(n - 1):
        idx_extremo = i
        for j in range(i + 1, n):
            cmp += 1
            if (not reversa and arr[j] < arr[idx_extremo]) or (reversa and arr[j] > arr[idx_extremo]):
                idx_extremo = j
        if idx_extremo != i:
            arr[i], arr[idx_extremo] = arr[idx_extremo], arr[i]
            intercambios += 1

    return ResultadoOrden(
        arreglo=arr, comparaciones=cmp, intercambios=intercambios,
        algoritmo="Selection Sort Descendente" if reversa else "Selection Sort",
        complejidad_t="O(n²)",
        complejidad_e="O(1)"
    )


# ══════════════════════════════════════════════════════════════════════════
#  3. INSERTION SORT
# ══════════════════════════════════════════════════════════════════════════

@_medir
def insertion_sort(arr: List[int], reversa: bool = False) -> ResultadoOrden:
    """
    Inserción: toma cada elemento y lo inserta en la posición correcta
    dentro de la parte ya ordenada (desplazando los mayores hacia la derecha).

    Mejor caso  : O(n)   — lista casi ordenada
    Peor / Med. : O(n²)
    Espacio     : O(1)   in-place, estable
    Ideal para n pequeño o como paso final en algoritmos híbridos (Timsort).
    """
    n   = len(arr)
    cmp = intercambios = 0

    for i in range(1, n):
        clave = arr[i]
        j = i - 1
        while j >= 0:
            cmp += 1
            if (not reversa and arr[j] > clave) or (reversa and arr[j] < clave):
                arr[j + 1] = arr[j]
                intercambios += 1
                j -= 1
            else:
                break
        arr[j + 1] = clave

    return ResultadoOrden(
        arreglo=arr, comparaciones=cmp, intercambios=intercambios,
        algoritmo="Insertion Sort Descendente" if reversa else "Insertion Sort",
        complejidad_t="O(n²) — O(n) mejor caso",
        complejidad_e="O(1)"
    )


# ══════════════════════════════════════════════════════════════════════════
#  4. SHELL SORT
# ══════════════════════════════════════════════════════════════════════════

@_medir
def shell_sort(arr: List[int], reversa: bool = False) -> ResultadoOrden:
    """
    Shell: generalización de Insertion Sort que permite intercambios de
    elementos lejanos. Comienza con un 'gap' grande (n/2) y lo va reduciendo
    hasta 1, momento en que equivale a Insertion Sort con lista casi ordenada.

    Complejidad : O(n log²n) con la secuencia de gap de Knuth
    Espacio     : O(1)  in-place, inestable
    """
    n   = len(arr)
    cmp = intercambios = 0

    # Secuencia de Knuth: 1, 4, 13, 40, 121, …
    gap = 1
    while gap < n // 3:
        gap = gap * 3 + 1

    while gap >= 1:
        for i in range(gap, n):
            temp = arr[i]
            j = i
            while j >= gap:
                cmp += 1
                if (not reversa and arr[j - gap] > temp) or (reversa and arr[j - gap] < temp):
                    arr[j] = arr[j - gap]
                    intercambios += 1
                    j -= gap
                else:
                    break
            arr[j] = temp
        gap //= 3

    return ResultadoOrden(
        arreglo=arr, comparaciones=cmp, intercambios=intercambios,
        algoritmo="Shell Sort Descendente" if reversa else "Shell Sort",
        complejidad_t="O(n log²n) — secuencia Knuth",
        complejidad_e="O(1)"
    )


# ══════════════════════════════════════════════════════════════════════════
#  5. MERGE SORT
# ══════════════════════════════════════════════════════════════════════════

@_medir
def merge_sort(arr: List[int], reversa: bool = False) -> ResultadoOrden:
    """
    Mezcla: divide el arreglo recursivamente a la mitad, ordena cada mitad
    y luego las fusiona en orden.

    Complejidad : O(n log n) en todos los casos
    Espacio     : O(n)  requiere arreglo auxiliar, estable
    Ideal para listas enlazadas y conjuntos de datos grandes y estables.
    """
    cmp_cnt      = [0]
    intercam_cnt = [0]

    def _merge(izq: List[int], der: List[int]) -> List[int]:
        resultado = []
        i = j = 0
        while i < len(izq) and j < len(der):
            cmp_cnt[0] += 1
            if (not reversa and izq[i] <= der[j]) or (reversa and izq[i] >= der[j]):
                resultado.append(izq[i])
                i += 1
            else:
                resultado.append(der[j])
                intercam_cnt[0] += 1
                j += 1
        resultado.extend(izq[i:])
        resultado.extend(der[j:])
        return resultado

    def _merge_sort_rec(a: List[int]) -> List[int]:
        if len(a) <= 1:
            return a
        mid = len(a) // 2
        return _merge(_merge_sort_rec(a[:mid]), _merge_sort_rec(a[mid:]))

    arr[:] = _merge_sort_rec(arr)

    return ResultadoOrden(
        arreglo=arr, comparaciones=cmp_cnt[0], intercambios=intercam_cnt[0],
        algoritmo="Merge Sort Descendente" if reversa else "Merge Sort",
        complejidad_t="O(n log n)",
        complejidad_e="O(n)"
    )


# ══════════════════════════════════════════════════════════════════════════
#  6. QUICK SORT
# ══════════════════════════════════════════════════════════════════════════

@_medir
def quick_sort(arr: List[int], reversa: bool = False) -> ResultadoOrden:
    """
    Rápido (Quick): selecciona un pivote, particiona el arreglo en elementos
    menores y mayores al pivote, y ordena ambas particiones recursivamente.
    Implementación iterativa con pila para evitar desbordamiento de pila.

    Mejor / Med.: O(n log n)
    Peor caso   : O(n²)  — pivote siempre el mayor/menor
    Espacio     : O(log n) pila implícita, inestable
    """
    cmp = intercambios = 0

    def _partition(lo: int, hi: int) -> int:
        nonlocal cmp, intercambios
        pivote = arr[hi]
        i = lo - 1
        for j in range(lo, hi):
            cmp += 1
            if (not reversa and arr[j] <= pivote) or (reversa and arr[j] >= pivote):
                i += 1
                arr[i], arr[j] = arr[j], arr[i]
                if i != j:
                    intercambios += 1
        arr[i + 1], arr[hi] = arr[hi], arr[i + 1]
        if i + 1 != hi:
            intercambios += 1
        return i + 1

    pila = [(0, len(arr) - 1)]
    while pila:
        lo, hi = pila.pop()
        if lo < hi:
            pi = _partition(lo, hi)
            pila.append((lo, pi - 1))
            pila.append((pi + 1, hi))

    return ResultadoOrden(
        arreglo=arr, comparaciones=cmp, intercambios=intercambios,
        algoritmo="Quick Sort Descendente" if reversa else "Quick Sort",
        complejidad_t="O(n log n) — O(n²) peor caso",
        complejidad_e="O(log n)"
    )


# ══════════════════════════════════════════════════════════════════════════
#  7. HEAP SORT
# ══════════════════════════════════════════════════════════════════════════

@_medir
def heap_sort(arr: List[int], reversa: bool = False) -> ResultadoOrden:
    """
    Montículo (Heap): construye un max-heap (o min-heap para descendente) y
    extrae repetidamente la raíz colocándola al final del arreglo.

    Complejidad : O(n log n) en todos los casos
    Espacio     : O(1)  in-place, inestable
    Garantiza O(n log n) en el peor caso (ventaja frente a Quick Sort).
    """
    n   = len(arr)
    cmp = intercambios = 0

    def _heapify(n_heap: int, raiz: int) -> None:
        nonlocal cmp, intercambios
        extremo = raiz
        izq   = 2 * raiz + 1
        der   = 2 * raiz + 2

        if izq < n_heap:
            cmp += 1
            if (not reversa and arr[izq] > arr[extremo]) or (reversa and arr[izq] < arr[extremo]):
                extremo = izq
        if der < n_heap:
            cmp += 1
            if (not reversa and arr[der] > arr[extremo]) or (reversa and arr[der] < arr[extremo]):
                extremo = der
        if extremo != raiz:
            arr[raiz], arr[extremo] = arr[extremo], arr[raiz]
            intercambios += 1
            _heapify(n_heap, extremo)

    # Fase 1: construir el heap
    for i in range(n // 2 - 1, -1, -1):
        _heapify(n, i)

    # Fase 2: extraer la raíz sucesivamente
    for i in range(n - 1, 0, -1):
        arr[0], arr[i] = arr[i], arr[0]
        intercambios += 1
        _heapify(i, 0)

    return ResultadoOrden(
        arreglo=arr, comparaciones=cmp, intercambios=intercambios,
        algoritmo="Heap Sort Descendente" if reversa else "Heap Sort",
        complejidad_t="O(n log n)",
        complejidad_e="O(1)"
    )


# ══════════════════════════════════════════════════════════════════════════
#  8. COUNTING SORT
# ══════════════════════════════════════════════════════════════════════════

@_medir
def counting_sort(arr: List[int], reversa: bool = False) -> ResultadoOrden:
    """
    Conteo (Counting): cuenta las ocurrencias de cada valor y reconstruye
    el arreglo en orden. No realiza comparaciones directas.

    Complejidad  : O(n + k)  donde k = rango de valores
    Espacio      : O(k)      arreglo de conteo, estable
    Restricción  : trabaja con enteros (acepta negativos vía offset).
    Ideal cuando k es pequeño relativamente a n.
    """
    if not arr:
        return ResultadoOrden(arreglo=[], algoritmo="Counting Sort",
                              complejidad_t="O(n + k)", complejidad_e="O(k)")

    # Convertir a int y aplicar offset para soportar negativos
    arr_int = [int(x) for x in arr]
    minimo  = min(arr_int)
    offset  = -minimo if minimo < 0 else 0
    arr_off = [v + offset for v in arr_int]

    k   = max(arr_off) + 1
    cnt = [0] * k

    for val in arr_off:       # fase de conteo
        cnt[val] += 1

    for i in range(1, k):     # prefijos acumulados (para estabilidad)
        cnt[i] += cnt[i - 1]

    salida = [0] * len(arr_off)
    for val in reversed(arr_off):  # recorrido inverso → estable
        cnt[val] -= 1
        salida[cnt[val]] = val

    # Quitar offset
    salida = [v - offset for v in salida]

    if reversa:
        salida.reverse()

    return ResultadoOrden(
        arreglo=salida, comparaciones=0, intercambios=0,
        algoritmo="Counting Sort Descendente" if reversa else "Counting Sort",
        complejidad_t="O(n + k)",
        complejidad_e=f"O(k)  [k = {k}]"
    )


# ══════════════════════════════════════════════════════════════════════════
#  9. RADIX SORT
# ══════════════════════════════════════════════════════════════════════════

@_medir
def radix_sort(arr: List[int], reversa: bool = False) -> ResultadoOrden:
    """
    Radix (Base): aplica Counting Sort dígito a dígito, del menos
    significativo (LSD) al más significativo.

    Complejidad : O(nk)  donde k = número de dígitos del máximo
    Espacio     : O(n + 10) por pasada, estable
    Ideal para enteros con rango acotado de dígitos.
    Soporta negativos vía offset.
    """
    if not arr:
        return ResultadoOrden(arreglo=[], algoritmo="Radix Sort",
                              complejidad_t="O(nk)", complejidad_e="O(n + k)")

    arr_int = [int(x) for x in arr]
    minimo  = min(arr_int)
    offset  = -minimo if minimo < 0 else 0
    arr     = [v + offset for v in arr_int]

    def _counting_por_digito(a: List[int], exp: int) -> List[int]:
        n      = len(a)
        salida = [0] * n
        cnt    = [0] * 10

        for val in a:
            digito = (val // exp) % 10
            cnt[digito] += 1

        for i in range(1, 10):
            cnt[i] += cnt[i - 1]

        for val in reversed(a):
            digito = (val // exp) % 10
            cnt[digito] -= 1
            salida[cnt[digito]] = val

        return salida

    maximo = max(arr) if arr else 0
    exp = 1
    while maximo // exp > 0:
        arr = _counting_por_digito(arr, exp)
        exp *= 10

    # Quitar offset
    arr = [v - offset for v in arr]

    if reversa:
        arr.reverse()

    return ResultadoOrden(
        arreglo=arr, comparaciones=0, intercambios=0,
        algoritmo="Radix Sort (LSD) Descendente" if reversa else "Radix Sort (LSD)",
        complejidad_t="O(nk)",
        complejidad_e="O(n + 10)"
    )


# ══════════════════════════════════════════════════════════════════════════
#  BÚSQUEDAS
# ══════════════════════════════════════════════════════════════════════════

from dataclasses import dataclass as _dataclass


@_dataclass
class ResultadoBusqueda:
    """Encapsula el resultado de una operación de búsqueda."""
    valor: float
    indices: List[int]
    encontrado: bool
    mensaje: str = ""


def busqueda_lineal(datos: List[float], valor: float) -> ResultadoBusqueda:
    """Recorre todos los elementos y devuelve todos los índices que coincidan."""
    indices = [i for i, elemento in enumerate(datos) if elemento == valor]
    return ResultadoBusqueda(
        valor=valor,
        indices=indices,
        encontrado=bool(indices),
        mensaje="Valor encontrado." if indices else "Valor no encontrado.",
    )


def busqueda_binaria(datos: List[float], valor: float) -> ResultadoBusqueda:
    """Búsqueda binaria sobre una lista ordenada; devuelve todos los índices coincidentes."""
    izquierda = 0
    derecha = len(datos) - 1

    while izquierda <= derecha:
        medio = (izquierda + derecha) // 2
        actual = datos[medio]
        if actual == valor:
            indices: List[int] = [medio]
            izquierdo = medio - 1
            while izquierdo >= 0 and datos[izquierdo] == valor:
                indices.insert(0, izquierdo)
                izquierdo -= 1
            derecho = medio + 1
            while derecho < len(datos) and datos[derecho] == valor:
                indices.append(derecho)
                derecho += 1
            return ResultadoBusqueda(
                valor=valor,
                indices=indices,
                encontrado=True,
                mensaje=f"Valor encontrado en {len(indices)} posición(es).",
            )
        if actual < valor:
            izquierda = medio + 1
        else:
            derecha = medio - 1

    return ResultadoBusqueda(
        valor=valor,
        indices=[],
        encontrado=False,
        mensaje="Valor no encontrado en la lista ordenada.",
    )


# ══════════════════════════════════════════════════════════════════════════
#  UTILIDADES
# ══════════════════════════════════════════════════════════════════════════

def comparar_todos(arr: List[int]) -> None:
    """Ejecuta todos los algoritmos sobre una copia del arreglo y muestra resultados."""
    algoritmos = [
        bubble_sort, selection_sort, insertion_sort, shell_sort,
        merge_sort, quick_sort, heap_sort, counting_sort, radix_sort,
    ]
    print("\n" + "═" * 48)
    print("  COMPARATIVA — ORDENAMIENTO INTERNO")
    print("═" * 48)
    print(f"  Entrada ({len(arr)} elementos): {arr}")
    print("═" * 48)
    for algo in algoritmos:
        print(algo(arr[:]))