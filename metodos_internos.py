"""
╔══════════════════════════════════════════════════════════════════════════╗
║          LIBRERÍA DE ORDENAMIENTO EXTERNO  — external_sorting.py         ║
║  Algoritmos diseñados para conjuntos de datos que NO caben en RAM.       ║
║  Operan sobre archivos en disco procesando bloques (chunks) a la vez.    ║
║                                                                          ║
║  Métodos incluidos:                                                      ║
║    1. Mezcla Directa          — bloques de tamaño fijo, k=2 vías         ║
║    2. Mezcla Natural          — detecta corridas naturales del archivo   ║
║    3. Mezcla Equilibrada      — distribuye corridas en k cintas pares    ║
║    4. Mezcla Polifásica       — distribución Fibonacci, k-1 cintas       ║
║    5. Selección por Sustitución — genera corridas largas con heap        ║
╚══════════════════════════════════════════════════════════════════════════╝

CONCEPTOS CLAVE
───────────────
• Corrida (run)  : secuencia de elementos ya ordenados dentro del archivo.
• Pasada (pass)  : lectura completa del archivo de entrada para fusionar.
• Cinta (tape)   : archivo auxiliar temporal que actúa como "cinta magnética".
• Chunk          : bloque de elementos que caben en RAM simultáneamente.

NOTA SOBRE SIMULACIÓN
─────────────────────
En una implementación real los datos están en disco y se procesan en bloques
de tamaño fijo (chunk_size). Aquí se simula con archivos temporales de texto
(un entero por línea) para que el comportamiento sea idéntico al real,
independientemente del tamaño del arreglo de entrada.
"""

from __future__ import annotations
import os
import heapq
import tempfile
import time
from dataclasses import dataclass, field
from typing import List, Iterator, Tuple, Optional


# ══════════════════════════════════════════════════════════════════════════
#  RESULTADO ESTÁNDAR
# ══════════════════════════════════════════════════════════════════════════

@dataclass
class ResultadoExterno:
    """Métricas de un algoritmo de ordenamiento externo."""
    arreglo:       List[int] = field(default_factory=list)
    algoritmo:     str   = ""
    pasadas:       int   = 0
    corridas_ini:  int   = 0   # corridas tras la fase de generación
    corridas_fin:  int   = 1   # siempre 1 al terminar (todo ordenado)
    lecturas:      int   = 0   # elementos leídos del disco
    escrituras:    int   = 0   # elementos escritos al disco
    comparaciones: int   = 0
    tiempo_ms:     float = 0.0
    chunk_size:    int   = 0
    descripcion:   str   = ""

    def __str__(self) -> str:
        sep = "─" * 52
        return (
            f"\n{sep}\n"
            f"  Algoritmo   : {self.algoritmo}\n"
            f"  Arreglo     : {self.arreglo}\n"
            f"  Chunk size  : {self.chunk_size} elementos/bloque\n"
            f"  Corridas ini: {self.corridas_ini}\n"
            f"  Pasadas     : {self.pasadas}\n"
            f"  Lecturas    : {self.lecturas}\n"
            f"  Escrituras  : {self.escrituras}\n"
            f"  Comparac.   : {self.comparaciones}\n"
            f"  Tiempo      : {self.tiempo_ms:.4f} ms\n"
            f"  Descripción : {self.descripcion}\n"
            f"{sep}"
        )


# ══════════════════════════════════════════════════════════════════════════
#  UTILIDADES INTERNAS DE MANEJO DE ARCHIVOS
# ══════════════════════════════════════════════════════════════════════════

class _CintaTemporal:
    """
    Abstracción de un archivo temporal que simula una cinta magnética.
    Almacena enteros, uno por línea.
    """

    def __init__(self):
        fd, self.ruta = tempfile.mkstemp(suffix=".cinta", prefix="ext_sort_")
        os.close(fd)

    # ── Escritura ─────────────────────────────────────────────────────────

    def escribir(self, datos: List[int]) -> int:
        """Escribe una lista de enteros al archivo. Retorna n° de elementos."""
        with open(self.ruta, "w") as f:
            for val in datos:
                f.write(f"{val}\n")
        return len(datos)

    def agregar(self, datos: List[int]) -> int:
        """Agrega enteros al final del archivo (modo append)."""
        with open(self.ruta, "a") as f:
            for val in datos:
                f.write(f"{val}\n")
        return len(datos)

    # ── Lectura ───────────────────────────────────────────────────────────

    def leer_todo(self) -> List[int]:
        """Lee todos los enteros del archivo en memoria."""
        with open(self.ruta, "r") as f:
            return [int(linea.strip()) for linea in f if linea.strip()]

    def leer_en_chunks(self, chunk_size: int) -> Iterator[List[int]]:
        """Genera chunks de hasta `chunk_size` elementos del archivo."""
        with open(self.ruta, "r") as f:
            chunk = []
            for linea in f:
                linea = linea.strip()
                if linea:
                    chunk.append(int(linea))
                    if len(chunk) == chunk_size:
                        yield chunk
                        chunk = []
            if chunk:
                yield chunk

    def iterador(self) -> Iterator[int]:
        """Itera elemento a elemento (simula lectura secuencial de cinta)."""
        with open(self.ruta, "r") as f:
            for linea in f:
                linea = linea.strip()
                if linea:
                    yield int(linea)

    def limpiar(self) -> None:
        """Vacía el contenido del archivo."""
        open(self.ruta, "w").close()

    def vacia(self) -> bool:
        return os.path.getsize(self.ruta) == 0

    def eliminar(self) -> None:
        try:
            os.remove(self.ruta)
        except FileNotFoundError:
            pass

    def __len__(self) -> int:
        return len(self.leer_todo())


def _escribir_datos_en_cinta(datos: List[int]) -> _CintaTemporal:
    """Crea una cinta temporal y escribe los datos en ella."""
    cinta = _CintaTemporal()
    cinta.escribir(datos)
    return cinta


# ══════════════════════════════════════════════════════════════════════════
#  1. MEZCLA DIRECTA (Direct Merge Sort)
# ══════════════════════════════════════════════════════════════════════════

def mezcla_directa(datos: List[int], chunk_size: int = 3) -> ResultadoExterno:
    """
    Mezcla Directa (2-way external merge sort):
    ─────────────────────────────────────────────
    FASE 1 — Generación de corridas:
      Lee bloques de `chunk_size` elementos, los ordena en RAM y escribe
      en cintas alternadas (A y B).

    FASE 2 — Fusión:
      Fusiona pares de corridas de A y B hacia C y D, alternando.
      Se repite duplicando el tamaño de corrida hasta que quede una sola.

    Complejidad: O(n log n) pasadas · O(n) por pasada = O(n log n)
    Cintas requeridas: 4 (2 entrada + 2 salida, se alternan roles)
    """
    inicio = time.perf_counter()
    res = ResultadoExterno(
        algoritmo="Mezcla Directa (2-way)",
        chunk_size=chunk_size,
        descripcion=(
            "Divide en bloques fijos → ordena en RAM → mezcla 2 cintas "
            "alternadas doblando el ancho en cada pasada."
        )
    )

    n = len(datos)
    if n == 0:
        res.arreglo = []
        return res

    # ── FASE 1: generar corridas ordenadas en dos cintas ──────────────────
    cinta_a = _CintaTemporal()
    cinta_b = _CintaTemporal()
    turno    = True   # True → cinta_a, False → cinta_b
    corridas = 0

    for i in range(0, n, chunk_size):
        bloque = sorted(datos[i : i + chunk_size])
        res.lecturas    += len(bloque)
        res.escrituras  += len(bloque)
        if turno:
            cinta_a.agregar(bloque)
        else:
            cinta_b.agregar(bloque)
        turno = not turno
        corridas += 1

    res.corridas_ini = corridas

    # ── FASE 2: mezcla iterativa ──────────────────────────────────────────
    ancho = chunk_size   # tamaño actual de corrida

    while ancho < n:
        res.pasadas += 1
        cinta_c = _CintaTemporal()
        cinta_d = _CintaTemporal()
        turno_sal = True

        iter_a = cinta_a.leer_en_chunks(ancho)
        iter_b = cinta_b.leer_en_chunks(ancho)

        for blq_a in iter_a:
            try:
                blq_b = next(iter_b)
            except StopIteration:
                blq_b = []

            # Fusión de dos corridas
            fusionado = []
            ia = ib = 0
            while ia < len(blq_a) and ib < len(blq_b):
                res.comparaciones += 1
                if blq_a[ia] <= blq_b[ib]:
                    fusionado.append(blq_a[ia]); ia += 1
                else:
                    fusionado.append(blq_b[ib]); ib += 1
            fusionado.extend(blq_a[ia:])
            fusionado.extend(blq_b[ib:])

            res.lecturas   += len(blq_a) + len(blq_b)
            res.escrituras += len(fusionado)

            if turno_sal:
                cinta_c.agregar(fusionado)
            else:
                cinta_d.agregar(fusionado)
            turno_sal = not turno_sal

        # Vaciar residuo de cinta_b si hay más corridas
        for blq_b in iter_b:
            if turno_sal:
                cinta_c.agregar(blq_b)
            else:
                cinta_d.agregar(blq_b)
            turno_sal = not turno_sal
            res.escrituras += len(blq_b)
            res.lecturas   += len(blq_b)

        # Rotar cintas
        cinta_a.eliminar(); cinta_b.eliminar()
        cinta_a = cinta_c
        cinta_b = cinta_d
        ancho *= 2

    # ── Leer resultado final ──────────────────────────────────────────────
    resultado = cinta_a.leer_todo()
    cinta_a.eliminar(); cinta_b.eliminar()

    res.arreglo   = resultado
    res.tiempo_ms = (time.perf_counter() - inicio) * 1000
    return res


def external_merge_sort(datos: List[int], output_file: str, chunk_size: int = 3) -> ResultadoExterno:
    """Ordenación externa simulada y escritura de resultado en un archivo."""
    res = mezcla_directa(datos, chunk_size=chunk_size)
    with open(output_file, "w", encoding="utf-8") as f:
        for valor in res.arreglo:
            f.write(f"{valor}\n")
    return res


# ══════════════════════════════════════════════════════════════════════════
#  2. MEZCLA NATURAL (Natural Merge Sort)
# ══════════════════════════════════════════════════════════════════════════

def mezcla_natural(datos: List[int], chunk_size: int = 3) -> ResultadoExterno:
    """
    Mezcla Natural:
    ───────────────
    FASE 1 — Detección de corridas:
      Recorre el archivo y detecta corridas *ya existentes* (secuencias
      ascendentes naturales). Las distribuye alternando en dos cintas.

    FASE 2 — Fusión:
      Fusiona pares de corridas naturales (sin longitud fija) hasta
      que queda una sola corrida. Si los datos tienen orden parcial,
      requiere menos pasadas que la Mezcla Directa.

    Complejidad: O(n log r) donde r = número de corridas iniciales
    Mejor caso : O(n)   — datos ya ordenados (1 sola corrida)
    Peor caso  : O(n log n) — datos en orden inverso
    """
    inicio = time.perf_counter()
    res = ResultadoExterno(
        algoritmo="Mezcla Natural",
        chunk_size=chunk_size,
        descripcion=(
            "Detecta corridas naturales en el archivo → las mezcla por pares "
            "hasta obtener una única corrida ordenada."
        )
    )

    n = len(datos)
    if n == 0:
        res.arreglo = []
        return res

    # ── FASE 1: detectar y distribuir corridas naturales ──────────────────
    def _detectar_corridas(lista: List[int]) -> List[List[int]]:
        if not lista:
            return []
        corridas = []
        run = [lista[0]]
        for i in range(1, len(lista)):
            res.lecturas += 1
            if lista[i] >= lista[i - 1]:
                run.append(lista[i])
            else:
                corridas.append(run)
                run = [lista[i]]
        corridas.append(run)
        return corridas

    corridas_actuales = _detectar_corridas(datos)
    res.corridas_ini  = len(corridas_actuales)

    while len(corridas_actuales) > 1:
        res.pasadas += 1
        nuevas_corridas = []

        for i in range(0, len(corridas_actuales), 2):
            izq = corridas_actuales[i]
            der = corridas_actuales[i + 1] if i + 1 < len(corridas_actuales) else []

            # Fusión
            fusionada = []
            ia = ib = 0
            res.lecturas += len(izq) + len(der)
            while ia < len(izq) and ib < len(der):
                res.comparaciones += 1
                if izq[ia] <= der[ib]:
                    fusionada.append(izq[ia]); ia += 1
                else:
                    fusionada.append(der[ib]); ib += 1
            fusionada.extend(izq[ia:])
            fusionada.extend(der[ib:])
            res.escrituras += len(fusionada)
            nuevas_corridas.append(fusionada)

        corridas_actuales = nuevas_corridas

    res.arreglo   = corridas_actuales[0] if corridas_actuales else []
    res.tiempo_ms = (time.perf_counter() - inicio) * 1000
    return res


# ══════════════════════════════════════════════════════════════════════════
#  3. MEZCLA EQUILIBRADA (Balanced Merge Sort — k vías)
# ══════════════════════════════════════════════════════════════════════════

def mezcla_equilibrada(datos: List[int], chunk_size: int = 3,
                       k: int = 4) -> ResultadoExterno:
    """
    Mezcla Equilibrada k-vías:
    ──────────────────────────
    Generaliza la Mezcla Directa a k cintas de entrada y k cintas de salida.
    En cada pasada fusiona hasta k corridas simultáneamente con un heap mínimo,
    reduciendo el número de pasadas a ⌈log_k(n/chunk_size)⌉.

    Complejidad: O(n log_k(n) · log k) ≈ O(n log n / log k)
    Cintas      : 2k
    Ventaja     : menos pasadas con k grande (a costa de más comparaciones/paso)
    """
    inicio = time.perf_counter()
    res = ResultadoExterno(
        algoritmo=f"Mezcla Equilibrada {k}-vías",
        chunk_size=chunk_size,
        descripcion=(
            f"Genera corridas de tamaño {chunk_size} → fusiona de {k} en {k} "
            "usando un heap mínimo → menos pasadas que la mezcla 2-vías."
        )
    )

    n = len(datos)
    if n == 0:
        res.arreglo = []
        return res

    # ── FASE 1: generar corridas en k cintas de entrada ───────────────────
    cintas_ent = [_CintaTemporal() for _ in range(k)]
    corridas   = 0

    for i, inicio_blq in enumerate(range(0, n, chunk_size)):
        bloque = sorted(datos[inicio_blq : inicio_blq + chunk_size])
        cintas_ent[corridas % k].agregar(bloque)
        res.lecturas   += len(bloque)
        res.escrituras += len(bloque)
        corridas += 1

    res.corridas_ini = corridas

    # ── FASE 2: fusión k-vías con heap ───────────────────────────────────
    ancho = chunk_size

    while ancho < n:
        res.pasadas  += 1
        cintas_sal    = [_CintaTemporal() for _ in range(k)]
        turno_sal     = 0

        # Obtener iteradores de chunks de cada cinta
        iters = [c.leer_en_chunks(ancho) for c in cintas_ent]

        while True:
            # Recoger una corrida de cada cinta disponible
            grupos = []
            for it in iters:
                try:
                    grupos.append(next(it))
                except StopIteration:
                    grupos.append([])

            if all(len(g) == 0 for g in grupos):
                break

            # Fusionar con heap
            heap  = []
            iters2 = [iter(g) for g in grupos]
            for ci, it2 in enumerate(iters2):
                try:
                    val = next(it2)
                    heapq.heappush(heap, (val, ci, it2))
                except StopIteration:
                    pass

            fusionado = []
            while heap:
                val, ci, it2 = heapq.heappop(heap)
                fusionado.append(val)
                res.comparaciones += 1
                try:
                    siguiente = next(it2)
                    heapq.heappush(heap, (siguiente, ci, it2))
                except StopIteration:
                    pass

            total_leid = sum(len(g) for g in grupos)
            res.lecturas   += total_leid
            res.escrituras += len(fusionado)
            cintas_sal[turno_sal].agregar(fusionado)
            turno_sal = (turno_sal + 1) % k

        for c in cintas_ent:
            c.eliminar()
        cintas_ent = cintas_sal
        ancho *= k

    # ── Recopilar resultado ───────────────────────────────────────────────
    resultado = []
    for c in cintas_ent:
        resultado.extend(c.leer_todo())
        c.eliminar()

    res.arreglo   = resultado
    res.tiempo_ms = (time.perf_counter() - inicio) * 1000
    return res


# ══════════════════════════════════════════════════════════════════════════
#  4. MEZCLA POLIFÁSICA (Polyphase Merge Sort)
# ══════════════════════════════════════════════════════════════════════════

def mezcla_polifasica(datos: List[int], chunk_size: int = 3,
                      k: int = 3) -> ResultadoExterno:
    """
    Mezcla Polifásica k-vías (Polyphase Merge Sort):
    ─────────────────────────────────────────────────
    Usa k cintas en total (k-1 de lectura + 1 de escritura que rota).
    Las corridas se distribuyen siguiendo números de Fibonacci generalizados,
    lo que maximiza la utilización de cintas y minimiza el número de pasadas
    respecto a la Mezcla Equilibrada con el mismo número de cintas.

    Complejidad: O(n log n) con menos pasadas que la Mezcla Equilibrada
    Cintas      : k  (vs 2k de la Mezcla Equilibrada)
    Ventaja     : usa la mitad de cintas para igual número de vías de mezcla

    Algoritmo de rotación:
      - k-1 cintas de entrada, 1 cinta de salida (vacía al inicio).
      - Se fusionan corridas hasta vaciar la cinta con menos corridas.
      - Esa cinta vacía se convierte en la nueva cinta de salida.
      - La cinta de salida anterior pasa a ser cinta de entrada.
      - Se repite hasta que solo una cinta tenga datos.
    """
    inicio = time.perf_counter()
    n_input = k - 1
    res = ResultadoExterno(
        algoritmo=f"Mezcla Polifásica {k}-cintas ({n_input} vías)",
        chunk_size=chunk_size,
        descripcion=(
            f"Distribuye corridas con números de Fibonacci en {n_input} cintas → "
            f"mezcla {n_input} vías hacia la cinta libre → rota cinta de salida."
        )
    )

    n = len(datos)
    if n == 0:
        res.arreglo = []
        return res

    # ── FASE 1: generar corridas ordenadas ───────────────────────────────
    corridas: List[List[int]] = []
    for i in range(0, n, chunk_size):
        bloque = sorted(datos[i : i + chunk_size])
        corridas.append(bloque)
        res.lecturas   += len(bloque)
        res.escrituras += len(bloque)

    res.corridas_ini = len(corridas)

    if len(corridas) == 1:
        res.arreglo   = corridas[0]
        res.tiempo_ms = (time.perf_counter() - inicio) * 1000
        return res

    # ── Distribución Fibonacci para n_input cintas ────────────────────────
    # Secuencia: dist[0] >= dist[1] >= ... >= dist[n_input-1]
    # Cada nivel: new[0] = sum(old), new[i] = old[i-1]
    def _fib_dist(n_runs: int, n_cintas: int) -> List[int]:
        dist = [1] + [0] * (n_cintas - 1)
        while sum(dist) < n_runs:
            new = [sum(dist)] + dist[:-1]
            dist = new
        return dist

    dist   = _fib_dist(len(corridas), n_input)
    dummies = sum(dist) - len(corridas)

    # ── Inicializar k cintas: n_input con datos + 1 vacía (salida) ───────
    # cintas[0..n_input-1] = entrada; cintas[n_input] = salida vacía
    cintas: List[List[List[int]]] = [[] for _ in range(k)]

    idx = 0
    for ci in range(n_input):
        for _ in range(dist[ci]):
            if dummies > 0:
                cintas[ci].append([])   # corrida ficticia (dummy)
                dummies -= 1
            elif idx < len(corridas):
                cintas[ci].append(corridas[idx])
                idx += 1

    cintas_entrada = list(range(n_input))
    cinta_salida   = n_input   # inicialmente vacía

    # ── FASE 2: mezcla polifásica con rotación ───────────────────────────
    limite = len(corridas) * k + 10   # salvaguarda anti-bucle infinito
    for _ in range(limite):
        # ¿Solo queda una cinta con datos?
        con_datos = [i for i in range(k) if cintas[i]]
        if len(con_datos) <= 1:
            break

        # Número de fusiones = corridas en la cinta más corta de las entradas
        min_runs = min(
            (len(cintas[i]) for i in cintas_entrada if cintas[i]),
            default=0
        )
        if min_runs == 0:
            break

        res.pasadas += 1

        for _ in range(min_runs):
            grupos = []
            for ci in cintas_entrada:
                if cintas[ci]:
                    grupos.append(cintas[ci].pop(0))

            # Fusionar grupos con heap mínimo
            heap:  List[Tuple] = []
            iters2 = [iter(g) for g in grupos]
            for ci2, it in enumerate(iters2):
                try:
                    val = next(it)
                    heapq.heappush(heap, (val, ci2, it))
                    res.lecturas += 1
                except StopIteration:
                    pass

            fusionado: List[int] = []
            while heap:
                val, ci2, it = heapq.heappop(heap)
                fusionado.append(val)
                res.comparaciones += 1
                try:
                    siguiente = next(it)
                    heapq.heappush(heap, (siguiente, ci2, it))
                    res.lecturas += 1
                except StopIteration:
                    pass

            res.escrituras += len(fusionado)
            cintas[cinta_salida].append(fusionado)

        # Rotar: la cinta de entrada que quedó vacía → nueva salida
        vacias = [i for i in cintas_entrada if not cintas[i]]
        if vacias:
            nueva_salida = vacias[0]
            cintas_entrada.remove(nueva_salida)
            cintas_entrada.append(cinta_salida)
            cinta_salida = nueva_salida

    # ── Recolectar resultado ──────────────────────────────────────────────
    resultado: List[int] = []
    for cinta in cintas:
        for run in cinta:
            resultado.extend(run)

    res.arreglo   = resultado
    res.tiempo_ms = (time.perf_counter() - inicio) * 1000
    return res


# ══════════════════════════════════════════════════════════════════════════
#  5. SELECCIÓN POR SUSTITUCIÓN (Replacement Selection Sort)
# ══════════════════════════════════════════════════════════════════════════

def seleccion_sustitucion(datos: List[int], chunk_size: int = 4) -> ResultadoExterno:
    """
    Selección por Sustitución (Replacement Selection):
    ───────────────────────────────────────────────────
    Genera corridas de longitud promedio 2·chunk_size (el doble que la
    Mezcla Directa básica) usando un heap mínimo de tamaño `chunk_size`.

    Algoritmo:
      1. Llena el heap con los primeros `chunk_size` elementos.
      2. Extrae el mínimo del heap → agrega a la corrida actual.
      3. Lee el siguiente elemento del archivo:
         • Si es ≥ al último extraído → entra al heap (misma corrida).
         • Si es <  al último extraído → va a un "heap fantasma" (nueva corrida).
      4. Al agotarse el heap activo, el heap fantasma se convierte en el nuevo heap.

    Complejidad: O(n log M) donde M = chunk_size
    Corridas generadas: ≈ n / (2·chunk_size) en datos aleatorios
    Uso: fase de generación de corridas para cualquier mezcla posterior.
    """
    inicio = time.perf_counter()
    res = ResultadoExterno(
        algoritmo="Selección por Sustitución",
        chunk_size=chunk_size,
        descripcion=(
            f"Heap de tamaño {chunk_size} genera corridas de longitud media "
            f"≈ 2·{chunk_size} = {2*chunk_size} en datos aleatorios."
        )
    )

    n = len(datos)
    if n == 0:
        res.arreglo = []
        return res

    heap_activo  : List[int] = []
    heap_fantasma: List[int] = []
    corridas     : List[List[int]] = []
    corrida_actual: List[int] = []
    ultimo_extraido = float('-inf')

    # Llenar heap inicial
    for i in range(min(chunk_size, n)):
        heapq.heappush(heap_activo, datos[i])
        res.lecturas += 1

    idx = chunk_size   # siguiente elemento a leer

    while heap_activo:
        # Extraer el mínimo
        minimo = heapq.heappop(heap_activo)
        corrida_actual.append(minimo)
        res.escrituras += 1
        ultimo_extraido = minimo

        # Leer siguiente elemento si quedan
        if idx < n:
            nuevo = datos[idx]
            res.lecturas += 1
            res.comparaciones += 1
            if nuevo >= ultimo_extraido:
                heapq.heappush(heap_activo, nuevo)
            else:
                heapq.heappush(heap_fantasma, nuevo)
            idx += 1

        # Si el heap activo se agota, iniciar nueva corrida
        if not heap_activo and heap_fantasma:
            corridas.append(corrida_actual)
            corrida_actual = []
            ultimo_extraido = float('-inf')
            heap_activo, heap_fantasma = heap_fantasma, []

    if corrida_actual:
        corridas.append(corrida_actual)

    res.corridas_ini = len(corridas)
    res.pasadas      = 1   # solo la fase de generación

    # ── Fusión final de las corridas generadas (2-vías simple) ───────────
    while len(corridas) > 1:
        res.pasadas += 1
        nuevas = []
        for i in range(0, len(corridas), 2):
            izq = corridas[i]
            der = corridas[i + 1] if i + 1 < len(corridas) else []
            fusionada = []
            ia = ib = 0
            res.lecturas += len(izq) + len(der)
            while ia < len(izq) and ib < len(der):
                res.comparaciones += 1
                if izq[ia] <= der[ib]:
                    fusionada.append(izq[ia]); ia += 1
                else:
                    fusionada.append(der[ib]); ib += 1
            fusionada.extend(izq[ia:])
            fusionada.extend(der[ib:])
            res.escrituras += len(fusionada)
            nuevas.append(fusionada)
        corridas = nuevas

    res.arreglo   = corridas[0] if corridas else []
    res.tiempo_ms = (time.perf_counter() - inicio) * 1000
    return res


# ══════════════════════════════════════════════════════════════════════════
#  UTILIDADES
# ══════════════════════════════════════════════════════════════════════════

def comparar_todos(datos: List[int], chunk_size: int = 4) -> None:
    """Ejecuta todos los algoritmos externos sobre los mismos datos."""
    algoritmos = [
        lambda d: mezcla_directa(d, chunk_size),
        lambda d: mezcla_natural(d, chunk_size),
        lambda d: mezcla_equilibrada(d, chunk_size, k=4),
        lambda d: mezcla_polifasica(d, chunk_size, k=3),
        lambda d: seleccion_sustitucion(d, chunk_size),
    ]
    print("\n" + "═" * 54)
    print("  COMPARATIVA — ORDENAMIENTO EXTERNO")
    print("═" * 54)
    print(f"  Entrada  ({len(datos)} elementos): {datos}")
    print(f"  Chunk    : {chunk_size} elementos/bloque")
    print("═" * 54)
    for algo in algoritmos:
        print(algo(datos[:]))