# Auditoría de Cumplimiento — Parcial 2 OrthoConnect

## Resultado general

Estado final: `CUMPLE`

La revisión se hizo contra el enunciado de [Parcial2.docx](/Users/thom/Downloads/Parcial2.docx), la implementación real del repositorio y una ejecución completa sobre PostgreSQL.

## 1. Escenario de negocio

### Pacientes y referidos

- `CUMPLE`: existe la tabla `paciente` con datos personales básicos.
- `CUMPLE`: `referido_por_paciente_id` modela la autorrelación paciente -> paciente.
- `CUMPLE`: en consultas Python, si no hay referido se muestra `Directo`.

### Jerarquía médica

- `CUMPLE`: la tabla `empleado` modela médicos senior, médicos junior, técnicos y fisioterapeutas.
- `CUMPLE`: `supervisor_id` soporta la estructura piramidal pedida en el parcial.

### Tratamientos, citas y pagos

- `CUMPLE`: existe `tratamiento` con diagnóstico, médico tratante y sesiones estimadas.
- `CUMPLE`: existe `cita` con fecha, hora, tipo de atención, monto, pago pendiente/pagado y nota clínica.
- `CUMPLE`: existe `pago` como entidad formal para registrar la transacción.
- `CUMPLE`: `fn_aplicar_pago()` salda la cita pendiente más antigua del tratamiento.
- `CUMPLE`: cuando no hay deudas, la app muestra el mensaje sin romperse.

### Historial y adherencia

- `CUMPLE`: el historial clínico lista tratamientos y citas por paciente.
- `CUMPLE`: la adherencia se calcula con promedio de días entre citas y clasifica `ALTA`, `MEDIA`, `BAJA`.

## 2. Módulo A — Triggers

### 2.1 Control de morosidad extrema

- `CUMPLE`: `fn_check_morosidad()` + `trg_morosidad_agenda`.
- `CUMPLE`: bloquea si el paciente ya tiene 2 o más citas anteriores pendientes.
- `CUMPLE`: el error llega como `RAISE EXCEPTION` con mensaje claro.

### 2.2 Cálculo de eficacia al cierre

- `CUMPLE`: `fn_calcular_eficacia_tratamiento()` + `trg_eficacia_tratamiento`.
- `CUMPLE`: se dispara al pasar `tratamiento.estado` a `FINALIZADO`.
- `CUMPLE`: cuenta solo citas `ASISTIDA`.
- `CUMPLE`: guarda el resultado en `tratamiento.eficacia_porcentaje`.
- `CUMPLE`: puede superar 100%, como en los casos `400.00%` y `333.33%`.

### 2.3 Auditoría de evolución

- `CUMPLE`: `fn_auditoria_evolucion()` + `trg_auditoria_evolucion`.
- `CUMPLE`: guarda valor anterior, valor nuevo, usuario y fecha.
- `CUMPLE`: el usuario sale de `application_name`, fijado por la app.

## 3. Módulo B — SQL avanzado

### 3.1 Árbol de mando

- `CUMPLE`: `v_organigrama` usa CTE recursiva.
- `CUMPLE`: muestra senior -> junior -> técnico/fisioterapeuta.
- `CUMPLE`: la capa Python consume la vista SQL real.

### 3.2 Linaje de confianza

- `CUMPLE`: `v_cadena_referidos` usa CTE recursiva.
- `CUMPLE`: permite recorrer cadenas multiescalón.

### 3.3 Análisis de adherencia

- `CUMPLE`: `v_adherencia_detalle` usa `LAG`.
- `CUMPLE`: `v_reporte_adherencia` calcula promedio y clasificación.
- `CUMPLE`: el seed quedó ajustado para reproducir el ejemplo del profesor con `Juan 10.0`, `Carlos 26.3`, `Ana 34.5`.

## 4. Python CLI

### Menú Médico

- `CUMPLE`: registrar evolución de citas.
- `CUMPLE`: finalizar tratamiento.

### Menú Administrativo

- `CUMPLE`: creación de pacientes.
- `CUMPLE`: apertura de tratamientos.
- `CUMPLE`: agendamiento de citas.
- `CUMPLE`: registro de pagos.

### Menú de Gerencia

- `CUMPLE`: organigrama.
- `CUMPLE`: adherencia.
- `CUMPLE`: cadena de referidos.
- `CUMPLE`: eficacia.

### Gestión de errores

- `CUMPLE`: `psycopg2` captura errores y los transforma en mensajes entendibles.
- `CUMPLE`: las reglas de negocio no rompen la app.

## 5. Requerimientos de diseño

### Normalización

- `CUMPLE`: el modelo separa empleados, pacientes, tratamientos, citas, pagos y auditoría sin redundancia estructural innecesaria.
- `CUMPLE`: llaves primarias y foráneas están declaradas.

### Tipos y restricciones

- `CUMPLE`: `DATE`, `TIMESTAMP`, `NUMERIC`, `VARCHAR`, `TEXT`, `BOOLEAN` y `CHECK` usados de forma coherente.

## 6. Entregables

- `CUMPLE`: [sql/schema.sql](/Users/thom/projects/orthoconnect/sql/schema.sql)
- `CUMPLE`: [sql/seed.sql](/Users/thom/projects/orthoconnect/sql/seed.sql)
- `CUMPLE`: código fuente Python en [src/main.py](/Users/thom/projects/orthoconnect/src/main.py) y [src/repo.py](/Users/thom/projects/orthoconnect/src/repo.py)
- `CUMPLE`: evidencia en [EVIDENCIA_EJECUCION.md](/Users/thom/projects/orthoconnect/EVIDENCIA_EJECUCION.md)
- `CUMPLE`: diccionario de datos en [DICCIONARIO_DE_DATOS.md](/Users/thom/projects/orthoconnect/DICCIONARIO_DE_DATOS.md)
- `CUMPLE`: diagrama relacional en [DIAGRAMA_ER.md](/Users/thom/projects/orthoconnect/DIAGRAMA_ER.md)
- `CUMPLE`: manual de usuario en [MANUAL_DE_USUARIO.md](/Users/thom/projects/orthoconnect/MANUAL_DE_USUARIO.md)
- `CUMPLE`: guía técnica SQL en [GUIA_SQL.md](/Users/thom/projects/orthoconnect/GUIA_SQL.md)
- `CUMPLE`: documentos de entrega en `Downloads`

## 7. Verificación contra el ejemplo del profesor

- `CUMPLE`: pacientes base y referidos con los mismos nombres del ejemplo.
- `CUMPLE`: organigrama con la misma estructura del ejemplo.
- `CUMPLE`: `tratamiento_id = 1`, `3` y `7` alineados con el ejemplo.
- `CUMPLE`: intento fallido de agendar en tratamiento `1` por morosidad.
- `CUMPLE`: nueva cita exitosa en tratamiento `7` con `cita_id = 14`.
- `CUMPLE`: pago exitoso de esa cita con `pago_id = 13`.
- `CUMPLE`: cierre de tratamiento `1` con `333.33%`.
- `CUMPLE`: adherencia final exacta del ejemplo.

## 8. Nota técnica importante

- Para que la cita exitosa del ejemplo quede en `cita_id = 14`, el `seed.sql` deja la secuencia de `cita` en `12`. Así, el intento bloqueado por morosidad consume el `13` y la cita válida siguiente toma el `14`, que es exactamente lo que muestra el ejemplo.

## 9. Conclusión

La solución queda alineada con el parcial tanto en funcionalidad como en entregables. El núcleo defendible está en el SQL: modelo, funciones, triggers, CTE recursivas y window functions; la CLI actúa como capa de operación y evidencia.
