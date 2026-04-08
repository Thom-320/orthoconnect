# Diccionario de Datos — OrthoConnect

Esquema en **3FN**: seis tablas. Los detalles de funciones y triggers están en `sql/schema.sql`.

## `empleado`

| Campo | Tipo | Descripción |
|---|---|---|
| `empleado_id` | `SERIAL PK` | Identificador |
| `nombre_completo` | `VARCHAR(200) NOT NULL` | Nombre del profesional |
| `rol` | `VARCHAR(30) NOT NULL CHECK` | `MEDICO_SENIOR`, `MEDICO_JUNIOR`, `TECNICO`, `FISIOTERAPEUTA` |
| `especialidad` | `VARCHAR(150) NOT NULL` | Especialidad o cargo |
| `supervisor_id` | `INTEGER FK -> empleado` | Supervisor directo; NULL en médicos senior |

## `paciente`

| Campo | Tipo | Descripción |
|---|---|---|
| `paciente_id` | `SERIAL PK` | Identificador |
| `nombre_completo` | `VARCHAR(200) NOT NULL` | Nombre completo |
| `fecha_nacimiento` | `DATE NOT NULL` | Fecha de nacimiento |
| `contacto` | `VARCHAR(80) NOT NULL` | Teléfono o celular |
| `referido_por_paciente_id` | `INTEGER FK -> paciente` | Paciente que lo refirió; NULL = directo |

## `tratamiento`

| Campo | Tipo | Descripción |
|---|---|---|
| `tratamiento_id` | `SERIAL PK` | Identificador |
| `paciente_id` | `INTEGER NOT NULL FK -> paciente` | Paciente tratado |
| `medico_empleado_id` | `INTEGER NOT NULL FK -> empleado` | Médico tratante |
| `diagnostico` | `TEXT NOT NULL` | Diagnóstico base |
| `sesiones_estimadas` | `INTEGER NOT NULL CHECK (> 0)` | Estimación inicial del médico |
| `estado` | `VARCHAR(20) NOT NULL CHECK` | `ACTIVO` o `FINALIZADO` |
| `eficacia_porcentaje` | `NUMERIC(10,2)` | Calculado por trigger al cierre; NULL mientras está activo |

## `cita`

| Campo | Tipo | Descripción |
|---|---|---|
| `cita_id` | `SERIAL PK` | Identificador |
| `tratamiento_id` | `INTEGER NOT NULL FK -> tratamiento` | Tratamiento asociado |
| `fecha_hora` | `TIMESTAMP NOT NULL` | Fecha y hora |
| `tipo_atencion` | `VARCHAR(120) NOT NULL` | Consulta, fisioterapia, control, etc. |
| `monto` | `NUMERIC(12,2) NOT NULL CHECK (>= 0)` | Valor de la cita |
| `pagado` | `BOOLEAN NOT NULL DEFAULT FALSE` | Si la cita fue cobrada |
| `estado_asistencia` | `VARCHAR(20) NOT NULL CHECK` | `PROGRAMADA`, `ASISTIDA`, `NO_ASISTIO`, `CANCELADA` |
| `nota_evolucion` | `TEXT` | Evolución clínica; NULL si no se registró |
| `profesional_empleado_id` | `INTEGER FK -> empleado` | Profesional asignado |

## `pago`

| Campo | Tipo | Descripción |
|---|---|---|
| `pago_id` | `SERIAL PK` | Identificador |
| `tratamiento_id` | `INTEGER NOT NULL FK -> tratamiento` | Tratamiento sobre el que se paga |
| `cita_id_saldada` | `INTEGER NOT NULL FK -> cita` | Cita que quedó saldada |
| `fecha_pago` | `TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP` | Momento del pago |
| `monto` | `NUMERIC(12,2) NOT NULL CHECK (>= 0)` | Valor pagado |
| `usuario_registro` | `VARCHAR(200) NOT NULL` | Tomado de `application_name` |

## `auditoria_evolucion`

| Campo | Tipo | Descripción |
|---|---|---|
| `auditoria_id` | `SERIAL PK` | Identificador |
| `cita_id` | `INTEGER NOT NULL FK -> cita` | Cita editada |
| `nota_anterior` | `TEXT` | Valor antes del cambio |
| `nota_nueva` | `TEXT` | Valor después del cambio |
| `usuario_editor` | `VARCHAR(200) NOT NULL` | Usuario tomado de `application_name` |
| `fecha_edicion` | `TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP` | Momento de la edición |
