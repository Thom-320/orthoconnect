# OrthoConnect — Cliente Python

Aplicación de consola (**Rich** + **psycopg2**) e interfaz gráfica opcional (**customtkinter**) para el sistema clínico OrthoConnect.

**Este repositorio contiene solo el cliente Python** (menús, integración, manejo de errores). El **SQL** (esquema, triggers, vistas, datos iniciales) lo aporta el equipo que modela la base de datos; véase [sql/README.md](sql/README.md) para el contrato esperado.

## Requisitos

- Python 3.11+ (recomendado)
- PostgreSQL con la base ya creada y los scripts del equipo BD aplicados
- En macOS, si la GUI falla por Tk: `brew install python-tk@<versión>`

## Instalación

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # y completar PG*
```

## Ejecución

Desde la raíz del proyecto:

```bash
PYTHONPATH=. python run.py
```

- Sin argumentos: elige CLI o GUI.
- `PYTHONPATH=. python run.py --cli` — solo consola.
- `PYTHONPATH=. python run.py --gui` — solo ventana.

También:

```bash
PYTHONPATH=. python -m src.main
PYTHONPATH=. python -m src.gui_main
```

## Pruebas

Requieren PostgreSQL accesible con la misma configuración que `.env`:

```bash
PYTHONPATH=. python -m unittest discover -s tests -v
```

Para omitir pruebas que hablan con la BD: `export ORTHCONNECT_SKIP_PG_TESTS=1`

## Cuándo se quitó el modo Demo

El modo “Demo sin base de datos” se eliminó **al separar responsabilidades**: el menú y la integración viven aquí; los datos y reglas en BD están en los scripts del otro equipo. La app **solo funciona contra PostgreSQL** una vez aplicado su SQL.
