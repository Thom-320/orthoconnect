# Evidencia de Ejecución — OrthoConnect

## Ambiente validado

- Fecha de validación: 2026-04-07
- Lenguaje: Python
- Base de datos: PostgreSQL
- Cliente: `psycopg2`
- Entrada principal: CLI en [src/main.py](/Users/thom/projects/orthoconnect/src/main.py)

## Evidencia automática

Se ejecutó la suite:

```bash
PYTHONPATH=. python -m unittest tests.test_e2e_demo tests.test_e2e_cli_smoke tests.test_e2e_postgres_optional -v
```

Resultado:

- `15` pruebas ejecutadas
- `15` OK
- `0` skipped

En el entorno final de validación también quedó verificada la GUI opcional: `customtkinter` está instalado, la ventana de login abre y las pantallas demo navegan sin errores.

## Casos validados sobre PostgreSQL real

### 1. Registro de paciente

Flujo ejecutado desde CLI:

- modo `PostgreSQL`
- operador `cli_demo`
- menú administrativo
- registro de paciente `Juan Perez`
- referido por paciente `7`

Resultado observado:

```text
✓  PACIENTE REGISTRADO  ·  ID: 9  ·  Juan Perez
```

## 2. Morosidad extrema

Flujo ejecutado:

- agendar cita para `tratamiento_id = 1`
- fecha `2026-03-25 10:00`

Resultado observado:

```text
REGLA DE NEGOCIO VIOLADA: BLOQUEO: El paciente tiene 2 citas anteriores pendientes. Debe ponerse al día.
```

Elemento técnico validado:

- trigger `trg_morosidad_agenda`
- función `fn_check_morosidad()`

## 3. Pago FIFO

Flujo ejecutado:

- agendar cita para `tratamiento_id = 7`
- fecha `2026-03-25 10:00`
- registrar pago sobre `tratamiento_id = 7`

Resultado observado en CLI:

```text
ID Pago:   13
ID Cita:   14
Fecha:     2026-03-25 10:00:00
Concepto:  Sesión Control
Monto:     $50000.00
```

Validación directa en base:

```text
PAGOS [(13, 7, 14, 'verificador'), ...]
```

Elemento técnico validado:

- función `fn_aplicar_pago()`
- tabla `pago`
- lógica FIFO sobre la cita pendiente más antigua

## 4. Evolución clínica y auditoría

Flujo ejecutado:

- registrar evolución sobre `cita_id = 3`
- nota: `Paciente completa sesion sin dolor.`

Resultado observado:

```text
✓  Evolución registrada
Auditoría guardada en base de datos.
```

Validación directa en base:

```text
AUDIT [(3, None, 'Paciente completa sesion sin dolor.', 'cli_demo'), ...]
```

Elemento técnico validado:

- actualización de `nota_evolucion`
- cambio automático de `estado_asistencia` a `ASISTIDA`
- trigger `trg_auditoria_evolucion`
- función `fn_auditoria_evolucion()`

## 5. Cierre de tratamiento y eficacia

Flujo ejecutado:

- finalizar `tratamiento_id = 1`

Resultado observado:

```text
✓  Tratamiento #1 cerrado
Eficacia calculada: 333.33%
```

Validación directa en base:

```text
TRAT [(1, 'FINALIZADO', Decimal('333.33')), ...]
```

Explicación del cálculo:

- sesiones estimadas: `10`
- sesiones asistidas reales: `3`
- eficacia: `10 / 3 * 100 = 333.33%`

Elemento técnico validado:

- trigger `trg_eficacia_tratamiento`
- función `fn_calcular_eficacia_tratamiento()`

## 6. Organigrama por CTE recursiva

Salida observada:

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

Elemento técnico validado:

- vista `v_organigrama`
- CTE recursiva senior → junior → técnico/fisioterapeuta

## 7. Cadena de referidos por CTE recursiva

Salida observada:

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

Elemento técnico validado:

- vista `v_cadena_referidos`
- CTE recursiva paciente → paciente

## 8. Adherencia con window functions

Salida observada:

```text
Juan Perez    10.0   MEDIA (Seguimiento)
Carlos Ruiz   26.3   BAJA (Riesgo de Abandono)
Ana Beltrán   34.5   BAJA (Riesgo de Abandono)
```

Elemento técnico validado:

- vista `v_adherencia_detalle` con `LAG`
- vista `v_reporte_adherencia` con promedio y clasificación

## 9. Validación automática específica sobre PostgreSQL

Las pruebas reales en [tests/test_e2e_postgres_optional.py](/Users/thom/projects/orthoconnect/tests/test_e2e_postgres_optional.py) cubren:

- bloqueo por morosidad al intentar una tercera deuda anterior
- pago FIFO con inserción en `pago`
- auditoría al modificar evolución
- cálculo de eficacia usando solo citas `ASISTIDA`
- consumo de vistas y reportes gerenciales

## Conclusión

La solución quedó validada contra los entregables del parcial:

- esquema SQL completo
- datos de prueba
- triggers
- funciones
- vistas analíticas
- CLI conectada con PostgreSQL
- manejo elegante de errores
- documentación coherente con el modelo real

Además, el `seed.sql` quedó ajustado para reproducir lo más fielmente posible el bloque de ejemplo del profesor:

- nombres con tildes y jerarquías esperadas
- `tratamiento_id = 1`, `3` y `7` alineados con el ejemplo
- pago exitoso sobre `cita_id = 14`
- cierre de tratamiento con `333.33%`
- adherencia final con `Juan 10.0`, `Carlos 26.3` y `Ana 34.5`
