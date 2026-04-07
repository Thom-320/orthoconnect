# Base de datos (responsabilidad del equipo de BD)

Los scripts **DDL/DML** (tablas, triggers, vistas, datos semilla) **no viven en este repositorio**. Los mantienen quienes diseñan el esquema y la lógica en PostgreSQL.

Antes de ejecutar la aplicación Python, deben crearse en su instancia de Postgres los objetos que esta app espera.

## Contrato mínimo con `src/repo.py`

La capa Python asume (nombres ilustrativos; deben coincidir con lo que entregue el equipo SQL):

- **Tablas:** `empleado`, `paciente`, `tratamiento`, `cita`, `auditoria_evolucion` con columnas alineadas a los `INSERT`/`UPDATE`/`SELECT` del repositorio.
- **Función:** `fn_aplicar_pago(integer)` devolviendo fila con cita saldada (FIFO), y mensajes de error reconocibles por la app (`INFO:NO_HAY_DEUDAS:` …).
- **Trigger de morosidad** en inserción de `cita` con `RAISE EXCEPTION` que contenga `BLOQUEO:` para bloqueo por deudas.
- **Vistas:** `v_reporte_adherencia`, `v_cadena_referidos` (y, si aplica, `v_organigrama` si el repo consulta esa vista en lugar de `empleado`).

Si el esquema cambia, actualicen **este README** o el README raíz con los nombres reales y el orden de aplicación de scripts.
