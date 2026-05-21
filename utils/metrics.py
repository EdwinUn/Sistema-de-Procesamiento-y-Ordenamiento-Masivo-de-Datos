from __future__ import annotations

import time
from functools import wraps
from typing import Callable


def medir_tiempo(func: Callable) -> Callable:
    """Decorador para medir el tiempo de ejecución de una función."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        inicio = time.perf_counter()
        resultado = func(*args, **kwargs)
        fin = time.perf_counter()
        if hasattr(resultado, "tiempo_ms"):
            setattr(resultado, "tiempo_ms", (fin - inicio) * 1000)
        return resultado

    return wrapper


def tiempo_ms(inicio: float, fin: float) -> float:
    return (fin - inicio) * 1000
