# OrthoConnect — Cliente Python

Aplicación **OrthoConnect v1.0**: menús de consola (**Rich** + **psycopg2**) e interfaz gráfica (**customtkinter**) para operar sobre la base clínica.

Este repositorio es el **cliente** (interfaz de usuario e integración). La **definición de la base de datos** (tablas, triggers, vistas, datos iniciales) la construyen **otros integrantes del equipo**; los archivos `.sql` se guardan **solo en cada máquina** dentro de `sql/` y **no se suben a GitHub** (ver `.gitignore`).

---

## Cómo repartimos el trabajo

| Quién | Qué hace |
|--------|-----------|
| **Thomas (este repo)** | Menú de usuario en Python, conexión con `psycopg2`, manejo de errores de negocio, modo **Demo** (sin base) para probar la app antes de que el SQL esté listo, GUI opcional, tests. |
| **Ospina, Sopa y quien modele la BD** | Estructura de **tablas**, **triggers**, **vistas**, funciones en PostgreSQL, y **datos semilla** (`schema.sql`, `seed.sql`). Deben entregar esos scripts al equipo (Drive, zip, otro repo, etc.) para que cada uno los copie en `sql/` en local. |

La frase *“el menú debería poder hacerse antes de tener la base bien diseñada”* se cumple con el **modo Demo**: corre la app con datos en memoria, sin PostgreSQL. La **integración real** (triggers, `fn_aplicar_pago`, vistas) solo funciona cuando PostgreSQL tiene **su** SQL aplicado.

---

## Qué tienen que hacer ustedes (equipo de base de datos)

1. **Entregar** los scripts acordados con el enunciado del curso (mínimo: tablas alineadas con lo que usa `src/repo.py`, triggers de morosidad / eficacia / auditoría si aplica, función de pago, vistas de informes).
2. **Documentar** brevemente nombres de tablas, función `fn_aplicar_pago` y vistas que expongan, para que no haya desajuste con el cliente.
3. Los demás copian esos archivos a **`sql/schema.sql`** y **`sql/seed.sql`** (o los nombres que acuerden) en su PC; esos archivos **no van al remoto** por diseño.

Si el esquema cambia, avisen para actualizar `src/repo.py` o el contrato de columnas.

---

## Requisitos

- **Python 3.11+** (recomendado; probado también con 3.14).
- **PostgreSQL** solo si van a usar el modo base real (no hace falta para Demo).
- **macOS:** si la GUI falla por Tk, instalar soporte gráfico, por ejemplo:
  ```bash
  brew install python-tk@3.14
  ```
  (ajustar la versión a la de su Python).

---

## Tutorial desde cero

### 1. Clonar el repositorio

```bash
git clone https://github.com/Thom-320/orthoconnect.git
cd orthoconnect
```

### 2. Crear entorno virtual e instalar dependencias

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Variables de entorno (solo para PostgreSQL)

```bash
cp .env.example .env
```

Editen `.env` con su host, puerto, nombre de base, usuario y contraseña. En Mac con Homebrew a veces **dejan `PGUSER` vacío** para usar el usuario del sistema.

**Importante:** el archivo `.env` no se sube a Git (está en `.gitignore`).

### 4. Scripts SQL (local, no en GitHub)

1. Obtengan `schema.sql` y `seed.sql` (u otros nombres) del equipo de base de datos.
2. Cópienlos en la carpeta **`sql/`** del proyecto, por ejemplo:
   - `sql/schema.sql`
   - `sql/seed.sql`

Esos `.sql` **no se commitean**; cada quien los tiene en su disco.

### 5. Crear la base y cargar datos (solo modo PostgreSQL)

```bash
createdb orthoconnect    # o el nombre que pusieron en PGDATABASE
psql -d orthoconnect -f sql/schema.sql
psql -d orthoconnect -f sql/seed.sql
```

(Ajusten usuario/host si `psql` lo requiere, por ejemplo `-U su_usuario -h localhost`.)

### 6. Ejecutar la aplicación

Desde la **raíz** del proyecto, con el venv activado:

```bash
export PYTHONPATH=.
python run.py
```

- Sin argumentos: pregunta si quieren **CLI** o **GUI**.
- Atajos:
  ```bash
  PYTHONPATH=. python run.py --cli
  PYTHONPATH=. python run.py --gui
  ```
- Equivalente directo:
  ```bash
  PYTHONPATH=. python -m src.main    # solo CLI
  PYTHONPATH=. python -m src.gui_main # solo GUI
  ```

### 7. Elegir modo al iniciar

- **CLI:** al arrancar, `1` = **Demo** (sin PostgreSQL, datos en memoria), `2` = **PostgreSQL** (necesita `.env` + SQL cargado).
- **GUI:** en el login, segmento **Demo (sin BD)** o **PostgreSQL**, luego nombre del operador e **Ingresar**.

El nombre del operador se usa como `application_name` en PostgreSQL (auditoría).

### 8. Probar que el código pasa tests (opcional)

```bash
PYTHONPATH=. python -m unittest discover -s tests -v
```

- Los tests de Demo no requieren base.
- Los que pegan a PostgreSQL **saltan** si no hay conexión o si definen:
  ```bash
  export ORTHCONNECT_SKIP_PG_TESTS=1
  ```

---

## Estructura útil del proyecto

```
orthoconnect/
├── run.py              # Lanzador CLI / GUI
├── .env.example        # Plantilla de conexión
├── requirements.txt
├── sql/                # Aquí van schema.sql y seed.sql SOLO en local
├── src/
│   ├── main.py         # CLI (Rich)
│   ├── gui_main.py     # GUI (customtkinter)
│   ├── db.py           # Conexión PostgreSQL
│   ├── repo.py         # Consultas y comandos SQL parametrizados
│   ├── repo_demo.py    # Misma API en memoria (modo Demo)
│   └── db_errors.py    # Mensajes claros para reglas de negocio
├── tests/              # Pruebas automáticas
└── frontend/           # Mock HTML (referencia visual, no conectado a la BD)
```

---

## Problemas frecuentes

| Síntoma | Qué revisar |
|---------|-------------|
| `ModuleNotFoundError: psycopg2` | `pip install -r requirements.txt` dentro del venv activado. |
| No conecta a PostgreSQL | `.env`, servicio Postgres arriba, BD creada, SQL aplicado. |
| `DemoCursor` / errores raros en GUI en Demo | Usar **Demo** con datos en memoria; no mezclar conexión Demo con SQL crudo en el mismo flujo (el código ya enruta a `repo_demo` en Demo). |
| GUI no abre en Mac | Instalar `python-tk` acorde a su versión de Python. |
| No ven `schema.sql` al clonar | Es normal: deben **copiarlo** desde quien tenga el SQL del curso. |

---

## Enlace del repositorio

**https://github.com/Thom-320/orthoconnect**

---

*Última actualización del README alineada con el reparto acordado: menú y cliente Python en este repo; esquema, triggers y datos en manos del equipo de base de datos, entregados fuera del remoto como archivos `.sql` locales.*
