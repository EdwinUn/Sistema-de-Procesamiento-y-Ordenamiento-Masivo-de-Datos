from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from gui.app import run_app
except ImportError as error:
    raise ImportError(
        "No se pudo iniciar la interfaz visual. Asegúrese de ejecutar el script desde la raíz del proyecto "
        "y de que el paquete gui exista." 
    ) from error


def main() -> None:
    run_app()


if __name__ == "__main__":
    main()
