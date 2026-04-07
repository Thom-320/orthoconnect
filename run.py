#!/usr/bin/env python3
"""
OrthoConnect — Lanzador
Uso:
    PYTHONPATH=. python run.py          # elige CLI o GUI en pantalla
    PYTHONPATH=. python run.py --cli    # fuerza CLI (rich)
    PYTHONPATH=. python run.py --gui    # fuerza GUI (customtkinter)
"""
import sys
import os


def main() -> None:
    args = sys.argv[1:]

    if "--cli" in args:
        _launch_cli()
    elif "--gui" in args:
        _launch_gui()
    else:
        # selector interactivo
        print()
        print("  ┌─────────────────────────────────┐")
        print("  │   ORTHOCONNECT v1.0              │")
        print("  │   ¿Cómo desea abrir la app?      │")
        print("  ├─────────────────────────────────┤")
        print("  │  1  Interfaz de consola  (CLI)   │")
        print("  │  2  Interfaz gráfica     (GUI)   │")
        print("  └─────────────────────────────────┘")
        print()
        opt = input("  Seleccione (1/2): ").strip()
        if opt == "2":
            _launch_gui()
        else:
            _launch_cli()


def _launch_cli() -> None:
    from src.main import main as cli_main
    sys.exit(cli_main())


def _launch_gui() -> None:
    from src.gui_main import main as gui_main
    gui_main()


if __name__ == "__main__":
    main()
