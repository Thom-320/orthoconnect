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
- `14` OK
- `1` skipped

La prueba omitida corresponde a la GUI opcional cuando `customtkinter` no está instalado. No afecta el entregable oficial del parcial, que se defiende con CLI + PostgreSQL.

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

- registrar pago sobre `tratamiento_id = 1`

Resultado observado en CLI:

```text
ID Pago:   13
ID Cita:   1
Fecha:     2026-03-01 08:00:00
Concepto:  Consulta inicial
Monto:     $80000.00
```

Validación directa en base:

```text
PAGOS [(13, 1, 1, 'cli_demo'), ...]
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
Eficacia calculada: 500.00%
```

Validación directa en base:

```text
TRAT [(1, 'FINALIZADO', Decimal('500.00')), ...]
```

Explicación del cálculo:

- sesiones estimadas: `10`
- sesiones asistidas reales: `2`
- eficacia: `10 / 2 * 100 = 500.00%`

Elemento técnico validado:

- trigger `trg_eficacia_tratamiento`
- función `fn_calcular_eficacia_tratamiento()`

## 6. Organigrama por CTE recursiva

Salida observada:

```text
└─ Dr. Gregory House  Ortopedia Senior
  └─ Dr. Shaun Murphy  Ortopedia Junior
    └─ Lic. Wilson  Fisioterapia
└─ Dra. Meredith Grey  Cirugia Ortopedica
  └─ Dra. Lexie Grey  Ortopedia General
  └─ Dr. George O'Malley  Traumatologia
└─ Dr. Derek Shepherd  Neuro-Ortopedia
  └─ Dr. Jackson Avery  Rehabilitacion
    └─ Ft. Jo Wilson  Fisioterapia Deportiva
    └─ Ft. April Kepner  Recuperacion Funcional
    └─ Ft. Ben Warren  Terapia Ocupacional
```

Elemento técnico validado:

- vista `v_organigrama`
- CTE recursiva senior → junior → técnico/fisioterapeuta

## 7. Cadena de referidos por CTE recursiva

Salida observada:

```text
Carlos Ruiz  (Directo)
  └─ Ana Beltran  via Carlos Ruiz
    └─ Luis Diaz  via Carlos Ruiz → Ana Beltran
      └─ James Rodriguez  via Carlos Ruiz → Ana Beltran → Luis Diaz
  └─ Sofia Vergara  via Carlos Ruiz
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
Ana Beltran   40.0   BAJA (Riesgo de Abandono)
Carlos Ruiz   34.5   BAJA (Riesgo de Abandono)
Juan Perez    17.0   BAJA (Riesgo de Abandono)
Luis Diaz      7.0   ALTA (Ideal)
Maria Lopez    3.5   ALTA (Ideal)
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
