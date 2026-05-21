from __future__ import annotations

import os
from pathlib import Path
from typing import Any, List

try:
    import pandas as pd
except ImportError:  # pragma: no cover
    pd = None

from config.settings import FORMATS_PERMITIDOS


def validar_extension(ruta: str) -> str:
    extension = Path(ruta).suffix.lower()
    if extension not in FORMATS_PERMITIDOS:
        raise ValueError(f"Extensión no soportada: {extension}. Use TXT o XLSX.")
    return extension


def cargar_datos(ruta: str) -> List[float]:
    ruta = ruta.strip()
    if not ruta:
        raise ValueError("La ruta no puede estar vacía.")

    if not os.path.exists(ruta):
        raise FileNotFoundError(f"No se encontró el archivo: {ruta}")

    extension = validar_extension(ruta)

    if extension == ".txt":
        return _cargar_txt(ruta)

    if extension == ".xlsx":
        return _cargar_xlsx(ruta)

    raise ValueError("Formato de archivo desconocido.")


def _cargar_txt(ruta: str) -> List[float]:
    datos: List[float] = []
    with open(ruta, "r", encoding="utf-8") as archivo:
        for linea in archivo:
            linea = linea.strip()
            if linea:
                try:
                    datos.append(float(linea))
                except ValueError as error:
                    raise ValueError(f"Valor no numérico en TXT: {linea}") from error
    return datos


def _cargar_xlsx(ruta: str) -> List[float]:
    if pd is None:
        raise ImportError(
            "pandas y openpyxl son necesarios para leer archivos XLSX."
        )

    datos: List[float] = []
    hoja = pd.read_excel(ruta, engine="openpyxl")

    if hoja.empty:
        return datos

    for fila in hoja.itertuples(index=False, name=None):
        for valor in fila:
            if valor is None:
                continue
            if isinstance(valor, (int, float)):
                datos.append(float(valor))
            else:
                try:
                    datos.append(float(str(valor).strip()))
                except ValueError as error:
                    raise ValueError(
                        f"Valor no numérico en XLSX: {valor}"
                    ) from error

    return datos


def exportar_resultados(datos: List[float], ruta: str) -> None:
    ruta = ruta.strip()
    if not ruta:
        raise ValueError("La ruta de exportación no puede estar vacía.")

    extension = validar_extension(ruta)

    if extension == ".txt":
        _exportar_txt(datos, ruta)
    elif extension == ".xlsx":
        _exportar_xlsx(datos, ruta)
    else:
        raise ValueError("Formato de exportación no soportado.")


def _exportar_txt(datos: List[float], ruta: str) -> None:
    with open(ruta, "w", encoding="utf-8") as archivo:
        for valor in datos:
            archivo.write(f"{valor}\n")


def _exportar_xlsx(datos: List[float], ruta: str) -> None:
    if pd is None:
        raise ImportError(
            "pandas y openpyxl son necesarios para exportar XLSX."
        )

    hoja = pd.DataFrame({"valor": datos})
    hoja.to_excel(ruta, index=False, engine="openpyxl")
