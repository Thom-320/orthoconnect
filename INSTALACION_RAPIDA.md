# Instalacion Rapida

## Opcion recomendada

Desde la raiz del repo:

```bash
make setup
cp .env.example .env
make reset-db
make test
```

Luego ejecutar:

```bash
PYTHONPATH=. .venv/bin/python -m src.main
```

## Que hace cada paso

### `make setup`

- crea `.venv` si no existe
- instala dependencias de `requirements.txt`

### `cp .env.example .env`

- deja lista la configuracion de PostgreSQL

### `make reset-db`

- ejecuta `sql/schema.sql`
- ejecuta `sql/seed.sql`

### `make test`

- corre toda la suite

## Si no tienes `make`

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env
PYTHONPATH=. .venv/bin/python scripts/reset_db.py
PYTHONPATH=. .venv/bin/python -m unittest discover -s tests -v
```
