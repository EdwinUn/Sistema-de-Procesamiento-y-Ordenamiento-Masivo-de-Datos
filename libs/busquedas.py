from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ResultadoBusqueda:
    valor: float
    indices: List[int]
    encontrado: bool
    mensaje: str = ""


def busqueda_lineal(datos: List[float], valor: float) -> ResultadoBusqueda:
    indices = [i for i, elemento in enumerate(datos) if elemento == valor]
    return ResultadoBusqueda(
        valor=valor,
        indices=indices,
        encontrado=bool(indices),
        mensaje="Valor encontrado." if indices else "Valor no encontrado."
    )


def busqueda_binaria(datos: List[float], valor: float) -> ResultadoBusqueda:
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
                mensaje=f"Valor encontrado en {len(indices)} posición(es)."
            )
        if actual < valor:
            izquierda = medio + 1
        else:
            derecha = medio - 1

    return ResultadoBusqueda(
        valor=valor,
        indices=[],
        encontrado=False,
        mensaje="Valor no encontrado en la lista ordenada."
    )
