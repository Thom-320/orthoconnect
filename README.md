# OrthoConnect

Entrega del **Proyecto Integrador / Parcial 2** de Ingeniería de Datos.

El repositorio contiene los entregables pedidos en el enunciado:

- `sql/schema.sql`: esquema, funciones, triggers y vistas
- `sql/seed.sql`: datos de prueba
- `src/main.py`: interfaz de línea de comando con `psycopg2`
- `src/repo.py`: acceso a datos SQL parametrizado
- documentación funcional y técnica
- pruebas automáticas sobre modo demo y PostgreSQL

## Alcance de la solución

El sistema modela la clínica **OrthoConnect** para rehabilitación de pacientes con lesiones óseas:

- Pacientes con cadena de referidos paciente → paciente
- Estructura jerárquica de empleados: médicos senior, médicos junior, técnicos y fisioterapeutas
- Tratamientos con sesiones estimadas y eficacia calculada al cierre
- Citas con estado de pago, estado de asistencia y nota de evolución
- Pagos FIFO sobre la cita pendiente más antigua del tratamiento
- Auditoría de cambios sobre la evolución clínica
- Reportes analíticos con CTE recursivas y window functions

## Requisitos

- Python 3.11+
- PostgreSQL 12+
- Dependencias de `requirements.txt`

Instalación:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

O más rápido:

```bash
make setup
```

## Configuración de PostgreSQL

Crear un archivo `.env` a partir de `.env.example`:

```bash
cp .env.example .env
```

Variables usadas:

- `PGHOST`
- `PGPORT`
- `PGDATABASE`
- `PGUSER`
- `PGPASSWORD`

## Cargar la base de datos

```bash
createdb orthoconnect
psql -d orthoconnect -f sql/schema.sql
psql -d orthoconnect -f sql/seed.sql
```

Atajo recomendado:

```bash
make reset-db
```

## Ejecutar la aplicación

CLI directa:

```bash
PYTHONPATH=. python -m src.main
```

Lanzador:

```bash
PYTHONPATH=. python run.py
```

La entrega está pensada para defenderse con **CLI + PostgreSQL**. La GUI queda como componente opcional.

## Menús implementados

### Módulo Administrativo

- Registrar nuevo paciente
- Abrir nuevo tratamiento
- Agendar cita
- Registrar pago

### Módulo Médico

- Registrar evolución de cita
- Finalizar tratamiento

### Módulo de Consultas

- Lista de pacientes
- Deudas de paciente
- Historial clínico
- Tratamientos por paciente

### Módulo Gerencial

- Organigrama
- Reporte de adherencia
- Cadena de referidos
- Reporte de eficacia

## Reglas de negocio implementadas

- **Morosidad extrema:** un trigger bloquea agendar una nueva cita si el paciente ya tiene dos o más citas anteriores pendientes.
- **Eficacia al cierre:** un trigger calcula `sesiones_estimadas / sesiones_asistidas * 100` cuando el tratamiento pasa a `FINALIZADO`.
- **Auditoría de evolución:** cada cambio de `nota_evolucion` guarda valor anterior, valor nuevo, usuario y fecha.
- **Pago FIFO:** `fn_aplicar_pago()` siempre salda la cita pendiente más antigua del tratamiento.

## Vistas analíticas

- `v_organigrama`: CTE recursiva de jerarquía de empleados
- `v_cadena_referidos`: CTE recursiva de cadena de referidos
- `v_adherencia_detalle`: intervalos entre citas usando `LAG`
- `v_reporte_adherencia`: promedio de días y clasificación `ALTA / MEDIA / BAJA`

## Pruebas

Ejecutar la suite:

```bash
PYTHONPATH=. python -m unittest discover -s tests -v
```

Con `make`:

```bash
make test
```

Cobertura actual:

- flujos del repositorio demo
- smoke test de CLI
- validaciones reales sobre PostgreSQL para morosidad, pagos, auditoría, eficacia y vistas

## Archivos de apoyo

- [DICCIONARIO_DE_DATOS.md](/Users/thom/projects/orthoconnect/DICCIONARIO_DE_DATOS.md)
- [DIAGRAMA_ER.md](/Users/thom/projects/orthoconnect/DIAGRAMA_ER.md)
- [MANUAL_DE_USUARIO.md](/Users/thom/projects/orthoconnect/MANUAL_DE_USUARIO.md)
- [EVIDENCIA_EJECUCION.md](/Users/thom/projects/orthoconnect/EVIDENCIA_EJECUCION.md)
- [GUIA_SQL.md](/Users/thom/projects/orthoconnect/GUIA_SQL.md)
- [INSTALACION_RAPIDA.md](/Users/thom/projects/orthoconnect/INSTALACION_RAPIDA.md)
