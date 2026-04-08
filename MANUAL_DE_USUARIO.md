# Manual de Usuario — OrthoConnect CLI

## 1. Objetivo

La aplicación permite operar la base de datos de la clínica OrthoConnect desde consola, cumpliendo los menús exigidos en el parcial:

- Administrativo
- Médico
- Consultas
- Gerencial

## 2. Inicio

Con la base ya cargada:

```bash
PYTHONPATH=. python -m src.main
```

Al iniciar se muestran dos modos:

- `1. Demo`
- `2. PostgreSQL`

Para la sustentación del parcial se debe usar **PostgreSQL**.

Luego se solicita el nombre del operador. Ese nombre se usa como `application_name` y queda registrado en auditoría y pagos.

## 3. Menú principal

Opciones:

1. Módulo Administrativo
2. Módulo Médico
3. Módulo de Consultas
4. Módulo Gerencial
5. Salir

## 4. Módulo Administrativo

### 4.1 Registrar Nuevo Paciente

Solicita:

- nombre completo
- fecha de nacimiento
- contacto
- si fue referido o no

Si fue referido, muestra la lista de pacientes para escoger el `paciente_id` del referidor.

### 4.2 Abrir Nuevo Tratamiento

Solicita:

- paciente
- médico tratante
- diagnóstico
- sesiones estimadas

El tratamiento queda en estado `ACTIVO`.

### 4.3 Agendar Cita

Solicita:

- tratamiento
- fecha y hora
- monto
- tipo de atención
- profesional

La cita queda con:

- `pagado = FALSE`
- `estado_asistencia = 'PROGRAMADA'`

Si el paciente ya tiene dos o más citas anteriores pendientes, PostgreSQL lanza una excepción y la aplicación la muestra como regla de negocio violada.

### 4.4 Registrar Pago

Solicita:

- `tratamiento_id`

La aplicación invoca `fn_aplicar_pago()`:

- busca la cita pendiente más antigua
- la marca como pagada
- crea el registro en `pago`
- devuelve `pago_id`, `cita_id`, fecha, concepto y monto

Si no hay deudas pendientes, el mensaje se muestra sin romper la aplicación.

## 5. Módulo Médico

### 5.1 Registrar Evolución de Cita

Solicita:

- `cita_id`
- nota de evolución

Además de guardar la nota, el sistema marca la cita como `ASISTIDA`.

Si la nota cambia, el trigger de auditoría guarda:

- valor anterior
- valor nuevo
- usuario editor
- fecha

### 5.2 Finalizar Tratamiento

Solicita:

- `tratamiento_id`

Al cambiar el estado a `FINALIZADO`, el trigger calcula la eficacia usando:

```text
sesiones_estimadas / sesiones_asistidas * 100
```

## 6. Módulo de Consultas

### 6.1 Lista de Pacientes

Muestra:

- ID
- nombre
- fecha de nacimiento
- contacto
- referido por / `Directo`

### 6.2 Deudas de Paciente

Muestra las citas no pagadas del paciente, con:

- cita
- tratamiento
- fecha
- tipo
- monto
- diagnóstico

### 6.3 Historial Clínico

Muestra por tratamiento:

- estado
- diagnóstico
- médico
- sesiones estimadas
- eficacia si ya existe

Y por cada cita:

- fecha
- tipo
- estado de pago
- estado de asistencia
- nota de evolución

### 6.4 Tratamientos por Paciente

Resume:

- estado del tratamiento
- diagnóstico
- médico
- sesiones estimadas
- número de citas
- citas asistidas
- eficacia

## 7. Módulo Gerencial

### 7.1 Organigrama

Consume `v_organigrama` y muestra la jerarquía completa de senior → junior → técnico/fisioterapeuta.

### 7.2 Reporte de Adherencia

Consume `v_reporte_adherencia` y muestra:

- paciente
- promedio de días entre citas
- clasificación `ALTA`, `MEDIA` o `BAJA`

### 7.3 Cadena de Referidos

Consume `v_cadena_referidos` y muestra el linaje de confianza entre pacientes.

### 7.4 Reporte de Eficacia

Muestra por tratamiento:

- paciente
- médico
- sesiones estimadas
- sesiones asistidas
- eficacia
- estado

## 8. Manejo de errores

La aplicación captura excepciones de PostgreSQL con `psycopg2` y las traduce a mensajes entendibles.

Casos importantes:

- morosidad al agendar
- intento de pago sin deudas
- tratamiento o cita inexistente

## 9. Flujo recomendado para la demo

1. Registrar paciente nuevo.
2. Consultar lista de pacientes para verificar el referido.
3. Intentar agendar una cita bloqueada por morosidad.
4. Registrar un pago FIFO.
5. Registrar evolución de una cita.
6. Finalizar tratamiento.
7. Mostrar organigrama, referidos y adherencia.
