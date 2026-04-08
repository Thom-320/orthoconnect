# Evidencia de Ejecución — OrthoConnect

## Ambiente validado

- Fecha de validación: 2026-04-07
- Lenguaje: Python
- Base de datos: PostgreSQL
- Cliente: `psycopg2`
- Entrada principal: CLI en [src/main.py](/Users/thom/projects/orthoconnect/src/main.py)

## Pruebas automáticas

Se corrió:

```bash
PYTHONPATH=. python -m unittest tests.test_e2e_demo tests.test_e2e_cli_smoke tests.test_e2e_postgres_optional -v
```

Resultado general:

- `15` pruebas ejecutadas
- `15` OK
- `0` skipped

También revisamos la GUI opcional. `customtkinter` está instalado, el login abre y las pantallas demo cargan sin error.

## Casos probados en PostgreSQL real

### 1. Registro de paciente

Lo que se probó:

- modo `PostgreSQL`
- operador `cli_demo`
- menú administrativo
- registro de paciente `Juan Perez`
- referido por paciente `7`

Resultado:

```text
✓  PACIENTE REGISTRADO  ·  ID: 9  ·  Juan Perez
```

### 2. Morosidad extrema

Lo que se probó:

- agendar cita para `tratamiento_id = 1`
- fecha `2026-03-25 10:00`

Resultado:

```text
REGLA DE NEGOCIO VIOLADA: BLOQUEO: El paciente tiene 2 citas anteriores pendientes. Debe ponerse al día.
```

Con esto se comprobó:

- trigger `trg_morosidad_agenda`
- función `fn_check_morosidad()`

### 3. Pago FIFO

Lo que se probó:

- agendar cita para `tratamiento_id = 7`
- fecha `2026-03-25 10:00`
- registrar pago sobre `tratamiento_id = 7`

Resultado en CLI:

```text
ID Pago:   13
ID Cita:   14
Fecha:     2026-03-25 10:00:00
Concepto:  Sesión Control
Monto:     $50000.00
```

Validación en base:

```text
PAGOS [(13, 7, 14, 'verificador'), ...]
```

Con esto se comprobó:

- función `fn_aplicar_pago()`
- tabla `pago`
- pago FIFO sobre la deuda más antigua

### 4. Evolución clínica y auditoría

Lo que se probó:

- registrar evolución sobre `cita_id = 3`
- nota: `Paciente completa sesion sin dolor.`

Resultado:

```text
✓  Evolución registrada
Auditoría guardada en base de datos.
```

Validación en base:

```text
AUDIT [(3, None, 'Paciente completa sesion sin dolor.', 'cli_demo'), ...]
```

Con esto se comprobó:

- actualización de `nota_evolucion`
- cambio automático de `estado_asistencia` a `ASISTIDA`
- trigger `trg_auditoria_evolucion`
- función `fn_auditoria_evolucion()`

### 5. Cierre de tratamiento y eficacia

Lo que se probó:

- finalizar `tratamiento_id = 1`

Resultado:

```text
✓  Tratamiento #1 cerrado
Eficacia calculada: 333.33%
```

Validación en base:

```text
TRAT [(1, 'FINALIZADO', Decimal('333.33')), ...]
```

Cálculo:

- sesiones estimadas: `10`
- sesiones asistidas reales: `3`
- eficacia: `10 / 3 * 100 = 333.33%`

Con esto se comprobó:

- trigger `trg_eficacia_tratamiento`
- función `fn_calcular_eficacia_tratamiento()`

### 6. Organigrama por CTE recursiva

Salida:

```text
└─ Dr. Gregory House  Ortopedia Senior
  └─ Dr. Shaun Murphy  Ortopedia Junior
    └─ Lic. Wilson  Fisioterapia
└─ Dra. Meredith Grey  Cirugía Ortopédica
  └─ Dra. Lexie Grey  Ortopedia General
  └─ Dr. George O'Malley  Traumatología
└─ Dr. Derek Shepherd  Neuro-Ortopedia
  └─ Dr. Jackson Avery  Rehabilitación
    └─ Ft. Jo Wilson  Fisioterapia Deportiva
    └─ Ft. April Kepner  Recuperación Funcional
    └─ Ft. Ben Warren  Terapia Ocupacional
```

Con esto se comprobó:

- vista `v_organigrama`
- CTE recursiva senior → junior → técnico/fisioterapeuta

### 7. Cadena de referidos por CTE recursiva

Salida:

```text
Carlos Ruiz  (Directo)
  └─ Ana Beltrán  via Carlos Ruiz
    └─ Luis Díaz  via Carlos Ruiz → Ana Beltrán
      └─ James Rodriguez  via Carlos Ruiz → Ana Beltrán → Luis Díaz
  └─ Sofía Vergara  via Carlos Ruiz
    └─ Juan Perez  via Carlos Ruiz → Sofía Vergara
Juan Perez  (Directo)
  └─ Maria Lopez  via Juan Perez
    └─ Pedro Gomez  via Juan Perez → Maria Lopez
```

Con esto se comprobó:

- vista `v_cadena_referidos`
- CTE recursiva paciente → paciente

### 8. Adherencia con window functions

Salida:

```text
Juan Perez    10.0   MEDIA (Seguimiento)
Carlos Ruiz   26.3   BAJA (Riesgo de Abandono)
Ana Beltrán   34.5   BAJA (Riesgo de Abandono)
```

Con esto se comprobó:

- vista `v_adherencia_detalle` con `LAG`
- vista `v_reporte_adherencia` con promedio y clasificación

## Validación automática específica sobre PostgreSQL

Además, las pruebas reales en [tests/test_e2e_postgres_optional.py](/Users/thom/projects/orthoconnect/tests/test_e2e_postgres_optional.py) cubren:

- bloqueo por morosidad al intentar una tercera deuda anterior
- pago FIFO con inserción en `pago`
- auditoría al modificar evolución
- cálculo de eficacia usando solo citas `ASISTIDA`
- consumo de vistas y reportes gerenciales

## Cierre

En resumen, se validó lo siguiente del parcial:

- esquema SQL completo
- datos de prueba
- triggers
- funciones
- vistas analíticas
- CLI conectada con PostgreSQL
- manejo de errores
- documentación del modelo

Además, el `seed.sql` se ajustó para que el ejemplo del profesor salga lo más parecido posible:

- nombres con tildes y jerarquías esperadas
- `tratamiento_id = 1`, `3` y `7` alineados con el ejemplo
- pago exitoso sobre `cita_id = 14`
- cierre de tratamiento con `333.33%`
- adherencia final con `Juan 10.0`, `Carlos 26.3` y `Ana 34.5`
