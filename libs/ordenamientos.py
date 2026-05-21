from __future__ import annotations

from dataclasses import dataclass
from typing import List

from utils.metrics import medir_tiempo


@dataclass
class ResultadoOrden:
    arreglo: List[float]
    algoritmo: str
    tiempo_ms: float = 0.0
    detalles: str = ""


@medir_tiempo
def ordenar_interno(datos: List[float], metodo: str = "bubble") -> ResultadoOrden:
    datos_copia = datos[:]
    if metodo == "bubble":
        return bubble_sort(datos_copia)
    if metodo == "insertion":
        return insertion_sort(datos_copia)
    if metodo == "merge":
        return merge_sort(datos_copia)
    raise ValueError(f"Método de ordenamiento interno desconocido: {metodo}")


@medir_tiempo
def ordenar_externo(datos: List[float], chunk_size: int = 1000) -> ResultadoOrden:
    if chunk_size < 1:
        raise ValueError("chunk_size debe ser un entero positivo.")

    if not datos:
        return ResultadoOrden(arreglo=[], algoritmo="Ordenamiento Externo", detalles="Sin datos.")

    corridas: List[List[float]] = []
    for inicio in range(0, len(datos), chunk_size):
        bloque = datos[inicio : inicio + chunk_size]
        corridas.append(_insertion_sort(bloque[:]))

    while len(corridas) > 1:
        fusionadas: List[List[float]] = []
        for i in range(0, len(corridas), 2):
            if i + 1 < len(corridas):
                fusionadas.append(_fusionar(corridas[i], corridas[i + 1]))
            else:
                fusionadas.append(corridas[i])
        corridas = fusionadas

    arreglo_ordenado = corridas[0] if corridas else []
    return ResultadoOrden(
        arreglo=arreglo_ordenado,
        algoritmo="Ordenamiento Externo (mezcla por bloques)",
        detalles=f"Chunk size={chunk_size}, chunks iniciales={len(corridas)}",
    )


def bubble_sort(datos: List[float]) -> ResultadoOrden:
    n = len(datos)
    for i in range(n - 1):
        intercambio = False
        for j in range(0, n - 1 - i):
            if datos[j] > datos[j + 1]:
                datos[j], datos[j + 1] = datos[j + 1], datos[j]
                intercambio = True
        if not intercambio:
            break
    return ResultadoOrden(arreglo=datos, algoritmo="Bubble Sort")


def insertion_sort(datos: List[float]) -> ResultadoOrden:
    n = len(datos)
    for i in range(1, n):
        clave = datos[i]
        j = i - 1
        while j >= 0 and datos[j] > clave:
            datos[j + 1] = datos[j]
            j -= 1
        datos[j + 1] = clave
    return ResultadoOrden(arreglo=datos, algoritmo="Insertion Sort")


def merge_sort(datos: List[float]) -> ResultadoOrden:
    if len(datos) <= 1:
        return ResultadoOrden(arreglo=datos, algoritmo="Merge Sort")

    medio = len(datos) // 2
    izquierda = merge_sort(datos[:medio]).arreglo
    derecha = merge_sort(datos[medio:]).arreglo
    resultado = _fusionar(izquierda, derecha)
    return ResultadoOrden(arreglo=resultado, algoritmo="Merge Sort")


def _fusionar(izquierda: List[float], derecha: List[float]) -> List[float]:
    resultado: List[float] = []
    i = j = 0
    while i < len(izquierda) and j < len(derecha):
        if izquierda[i] <= derecha[j]:
            resultado.append(izquierda[i])
            i += 1
        else:
            resultado.append(derecha[j])
            j += 1
    resultado.extend(izquierda[i:])
    resultado.extend(derecha[j:])
    return resultado


def _insertion_sort(datos: List[float]) -> List[float]:
    return insertion_sort(datos).arreglo
