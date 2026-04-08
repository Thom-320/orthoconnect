# Diccionario de Datos — OrthoConnect

## Resumen del modelo

El esquema está normalizado a **3FN** y separa claramente:

- personas del equipo clínico (`empleado`)
- pacientes (`paciente`)
- tratamientos (`tratamiento`)
- citas (`cita`)
- pagos (`pago`)
- auditoría clínica (`auditoria_evolucion`)

## Tabla `empleado`

| Campo | Tipo | Restricciones | Descripción |
|---|---|---|---|
| `empleado_id` | `SERIAL` | `PK` | Identificador del empleado |
| `nombre_completo` | `VARCHAR(200)` | `NOT NULL` | Nombre visible del profesional |
| `rol` | `VARCHAR(30)` | `NOT NULL`, `CHECK` | `MEDICO_SENIOR`, `MEDICO_JUNIOR`, `TECNICO`, `FISIOTERAPEUTA` |
| `especialidad` | `VARCHAR(150)` | `NOT NULL` | Especialidad o cargo |
| `supervisor_id` | `INTEGER` | `FK -> empleado.empleado_id` | Supervisor directo |

## Tabla `paciente`

| Campo | Tipo | Restricciones | Descripción |
|---|---|---|---|
| `paciente_id` | `SERIAL` | `PK` | Identificador del paciente |
| `nombre_completo` | `VARCHAR(200)` | `NOT NULL` | Nombre completo |
| `fecha_nacimiento` | `DATE` | `NOT NULL` | Fecha de nacimiento |
| `contacto` | `VARCHAR(80)` | `NOT NULL` | Teléfono o celular |
| `referido_por_paciente_id` | `INTEGER` | `FK -> paciente.paciente_id` | Paciente que lo refirió; `NULL` implica `Directo` |

## Tabla `tratamiento`

| Campo | Tipo | Restricciones | Descripción |
|---|---|---|---|
| `tratamiento_id` | `SERIAL` | `PK` | Identificador del tratamiento |
| `paciente_id` | `INTEGER` | `NOT NULL`, `FK -> paciente.paciente_id` | Paciente tratado |
| `medico_empleado_id` | `INTEGER` | `NOT NULL`, `FK -> empleado.empleado_id` | Médico tratante |
| `diagnostico` | `TEXT` | `NOT NULL` | Diagnóstico base |
| `sesiones_estimadas` | `INTEGER` | `NOT NULL`, `CHECK (sesiones_estimadas > 0)` | Sesiones estimadas por el médico |
| `estado` | `VARCHAR(20)` | `NOT NULL`, `CHECK` | `ACTIVO` o `FINALIZADO` |
| `eficacia_porcentaje` | `NUMERIC(10,2)` | `NULL` | Resultado calculado al cierre |

## Tabla `cita`

| Campo | Tipo | Restricciones | Descripción |
|---|---|---|---|
| `cita_id` | `SERIAL` | `PK` | Identificador de la cita |
| `tratamiento_id` | `INTEGER` | `NOT NULL`, `FK -> tratamiento.tratamiento_id` | Tratamiento asociado |
| `fecha_hora` | `TIMESTAMP` | `NOT NULL` | Fecha y hora de la cita |
| `tipo_atencion` | `VARCHAR(120)` | `NOT NULL` | Consulta, control, fisioterapia, etc. |
| `monto` | `NUMERIC(12,2)` | `NOT NULL`, `CHECK (monto >= 0)` | Valor de la cita |
| `pagado` | `BOOLEAN` | `NOT NULL`, `DEFAULT FALSE` | Estado de pago |
| `estado_asistencia` | `VARCHAR(20)` | `NOT NULL`, `CHECK` | `PROGRAMADA`, `ASISTIDA`, `NO_ASISTIO`, `CANCELADA` |
| `nota_evolucion` | `TEXT` | `NULL` | Evolución clínica de la cita |
| `profesional_empleado_id` | `INTEGER` | `FK -> empleado.empleado_id` | Profesional que atendió o atendrá |

## Tabla `pago`

| Campo | Tipo | Restricciones | Descripción |
|---|---|---|---|
| `pago_id` | `SERIAL` | `PK` | Identificador del pago |
| `tratamiento_id` | `INTEGER` | `NOT NULL`, `FK -> tratamiento.tratamiento_id` | Tratamiento sobre el que se paga |
| `cita_id_saldada` | `INTEGER` | `NOT NULL`, `FK -> cita.cita_id` | Cita que quedó saldada |
| `fecha_pago` | `TIMESTAMP` | `NOT NULL`, `DEFAULT CURRENT_TIMESTAMP` | Momento del pago |
| `monto` | `NUMERIC(12,2)` | `NOT NULL`, `CHECK (monto >= 0)` | Valor pagado |
| `usuario_registro` | `VARCHAR(200)` | `NOT NULL` | Usuario tomado desde `application_name` |

## Tabla `auditoria_evolucion`

| Campo | Tipo | Restricciones | Descripción |
|---|---|---|---|
| `auditoria_id` | `SERIAL` | `PK` | Identificador de auditoría |
| `cita_id` | `INTEGER` | `NOT NULL`, `FK -> cita.cita_id` | Cita editada |
| `nota_anterior` | `TEXT` | `NULL` | Valor anterior |
| `nota_nueva` | `TEXT` | `NULL` | Valor nuevo |
| `usuario_editor` | `VARCHAR(200)` | `NOT NULL` | Usuario que hizo el cambio |
| `fecha_edicion` | `TIMESTAMP` | `NOT NULL`, `DEFAULT CURRENT_TIMESTAMP` | Momento de edición |

## Índices principales

- `idx_empleado_supervisor`
- `idx_paciente_referido`
- `idx_tratamiento_paciente`
- `idx_tratamiento_estado`
- `idx_cita_tratamiento_fecha`
- `idx_cita_pendiente`
- `idx_pago_tratamiento`
- `idx_auditoria_cita`

## Funciones y triggers

### `fn_check_morosidad()` + `trg_morosidad_agenda`

- Tipo: `BEFORE INSERT ON cita`
- Regla: bloquea el agendamiento si el paciente ya tiene **2 o más citas anteriores no pagadas**
- Resultado: `RAISE EXCEPTION` con mensaje legible

### `fn_calcular_eficacia_tratamiento()` + `trg_eficacia_tratamiento`

- Tipo: `BEFORE UPDATE OF estado ON tratamiento`
- Regla: al pasar a `FINALIZADO`, calcula:

```sql
(sesiones_estimadas / sesiones_asistidas) * 100
```

- Solo cuenta citas con `estado_asistencia = 'ASISTIDA'`

### `fn_auditoria_evolucion()` + `trg_auditoria_evolucion`

- Tipo: `AFTER UPDATE OF nota_evolucion ON cita`
- Regla: guarda `OLD`, `NEW`, usuario y fecha

### `fn_aplicar_pago(p_tratamiento_id)`

- Busca la cita pendiente más antigua del tratamiento
- La marca como pagada
- Inserta la transacción en `pago`
- Retorna:
  - `pago_id_registrado`
  - `cita_id_pagada`
  - `fecha_hora_cita`
  - `tipo_atencion_pago`
  - `monto_pagado`

## Vistas analíticas

### `v_organigrama`

CTE recursiva para recorrer la jerarquía completa desde los médicos senior hacia juniors, técnicos y fisioterapeutas.

Campos:

- `empleado_id`
- `nombre_completo`
- `rol`
- `especialidad`
- `supervisor_id`
- `nivel`
- `ruta_orden`

### `v_cadena_referidos`

CTE recursiva sobre `paciente.referido_por_paciente_id` para reconstruir el linaje de confianza.

Campos:

- `paciente_id`
- `nombre_completo`
- `referido_por_paciente_id`
- `nivel`
- `cadena_texto`

### `v_adherencia_detalle`

Window function con `LAG` para medir el intervalo entre citas del paciente en orden cronológico.

Campos:

- `paciente_id`
- `nombre_completo`
- `tratamiento_id`
- `cita_id`
- `fecha_hora`
- `fecha_previa`
- `dias_desde_cita_previa`

### `v_reporte_adherencia`

Resumen por paciente con promedio de días entre citas y clasificación:

- `ALTA (Ideal)` si `<= 7`
- `MEDIA (Seguimiento)` si `<= 15`
- `BAJA (Riesgo de Abandono)` en otro caso
