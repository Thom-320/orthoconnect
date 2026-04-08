# Guia SQL para el Equipo

Este archivo explica el contrato SQL que usa el proyecto y el orden recomendado para trabajar.

## 1. Archivos que importan

- [sql/schema.sql](/Users/thom/projects/orthoconnect/sql/schema.sql)
- [sql/seed.sql](/Users/thom/projects/orthoconnect/sql/seed.sql)

`schema.sql` crea:

- tablas
- indices
- funciones PL/pgSQL
- triggers
- vistas analiticas

`seed.sql` carga un conjunto de datos base para:

- probar morosidad
- probar pago FIFO
- probar eficacia
- mostrar organigrama
- mostrar referidos
- mostrar adherencia

Importante:

- No hay un dataset oficial adjunto en el parcial.
- Los datos de `seed.sql` son sinteticos y fueron armados para cubrir los escenarios del enunciado y reproducir los ejemplos del profesor.
- Algunos nombres y flujos salen casi directos del bloque de ejemplo del documento del parcial; otros registros adicionales se inventaron para completar casos de prueba.

## 2. Orden de carga

Siempre ejecutar en este orden:

```bash
psql -d orthoconnect -f sql/schema.sql
psql -d orthoconnect -f sql/seed.sql
```

Si cambian el esquema, vuelvan a cargar ambos archivos.

Para la sustentacion y para reproducir el ejemplo textual del profesor, conviene resetear la base justo antes de la demo:

```bash
make reset-db
```

## 3. Tablas principales

### `empleado`

Representa la jerarquia clinica.

- `rol`: `MEDICO_SENIOR`, `MEDICO_JUNIOR`, `TECNICO`, `FISIOTERAPEUTA`
- `supervisor_id`: autorrelacion para el arbol de mando

### `paciente`

- guarda los datos base del paciente
- `referido_por_paciente_id` enlaza el linaje de confianza paciente -> paciente

### `tratamiento`

- pertenece a un paciente
- tiene un medico tratante
- guarda sesiones estimadas
- guarda `eficacia_porcentaje` calculada por trigger

### `cita`

Separar estos dos conceptos es clave:

- `pagado`: si la cita fue pagada
- `estado_asistencia`: si la cita fue asistida

Eso evita mezclar operacion clinica con cobranza.

### `pago`

Tabla independiente para trazabilidad financiera:

- que tratamiento recibio el pago
- que cita quedo saldada
- quien registro el pago
- cuando se hizo

### `auditoria_evolucion`

Registra cada cambio en `nota_evolucion`.

## 4. Triggers y funciones

### Morosidad

Función:

- `fn_check_morosidad()`

Trigger:

- `trg_morosidad_agenda`

Regla:

- no se puede insertar una nueva cita si el paciente ya tiene 2 o mas citas anteriores sin pagar

### Eficacia

Función:

- `fn_calcular_eficacia_tratamiento()`

Trigger:

- `trg_eficacia_tratamiento`

Regla:

- al pasar un tratamiento a `FINALIZADO`, calcula:

```text
sesiones_estimadas / sesiones_asistidas * 100
```

Solo cuentan citas con `estado_asistencia = 'ASISTIDA'`.

### Auditoria

Función:

- `fn_auditoria_evolucion()`

Trigger:

- `trg_auditoria_evolucion`

Regla:

- cada cambio de `nota_evolucion` guarda `OLD`, `NEW`, usuario y fecha

### Pago FIFO

Función:

- `fn_aplicar_pago(p_tratamiento_id)`

Regla:

- paga la cita pendiente mas antigua del tratamiento
- marca la cita como pagada
- inserta el registro en `pago`

## 5. Vistas

### `v_organigrama`

- CTE recursiva de empleados
- devuelve `nivel` y `ruta_orden`

### `v_cadena_referidos`

- CTE recursiva de pacientes
- permite reconstruir toda la cadena

### `v_adherencia_detalle`

- usa `LAG`
- calcula dias entre citas del paciente en orden cronologico

### `v_reporte_adherencia`

- resume por paciente
- clasifica `ALTA`, `MEDIA`, `BAJA`

## 6. Contrato con Python

El cliente Python espera:

- `fn_aplicar_pago()` devuelva `pago_id`, `cita_id`, `fecha`, `tipo`, `monto`
- `historial_clinico()` incluya `pagado` y `estado_asistencia`
- `organigrama_empleados()` lea desde `v_organigrama`
- `reporte_adherencia()` lea desde `v_reporte_adherencia`

Si cambian esas salidas, deben ajustar [src/repo.py](/Users/thom/projects/orthoconnect/src/repo.py) y [src/main.py](/Users/thom/projects/orthoconnect/src/main.py).

## 7. Consultas utiles para defensa

Ver pagos registrados:

```sql
SELECT * FROM pago ORDER BY pago_id;
```

Ver auditoria:

```sql
SELECT * FROM auditoria_evolucion ORDER BY auditoria_id DESC;
```

Ver adherencia detalle:

```sql
SELECT * FROM v_adherencia_detalle ORDER BY paciente_id, fecha_hora;
```

Ver organigrama:

```sql
SELECT * FROM v_organigrama ORDER BY ruta_orden;
```

## 8. Regla de trabajo para el equipo

Si alguien toca SQL:

1. editar `schema.sql` o `seed.sql`
2. recargar base
3. correr tests
4. validar una ejecucion CLI

Comando recomendado:

```bash
make reset-db
make test
```

