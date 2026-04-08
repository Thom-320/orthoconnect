# Evidencia de Ejecución — OrthoConnect

Validado el 7 de abril de 2026 sobre PostgreSQL con `psycopg2`.

Suite de pruebas:

```bash
PYTHONPATH=. python -m unittest tests.test_e2e_demo tests.test_e2e_cli_smoke tests.test_e2e_postgres_optional -v
```

Resultado: **15 pruebas, 15 OK, 0 skipped.**

---

## 1. Registro de paciente referido

Se registró `Juan Perez` como referido por Sofía Vergara (paciente 7):

```text
✓  PACIENTE REGISTRADO  ·  ID: 9  ·  Juan Perez
```

---

## 2. Control de morosidad

Intento de agendar en el tratamiento 1 (paciente con 2 citas sin pagar):

```text
REGLA DE NEGOCIO VIOLADA: BLOQUEO: El paciente tiene 2 citas anteriores pendientes. Debe ponerse al día.
```

La aplicación muestra el mensaje y vuelve al menú sin cerrarse.

---

## 3. Agendamiento y pago FIFO

Se agendó una cita para el tratamiento 7 y luego se registró el pago:

```text
ID Pago:   13
ID Cita:   14
Fecha:     2026-03-25 10:00:00
Concepto:  Sesión Control
Monto:     $50000.00
```

Nota: el intento fallido del caso anterior consumió el ID 13 de la secuencia `cita` (las secuencias en PostgreSQL no hacen rollback), por eso la cita exitosa queda con el ID 14.

---

## 4. Evolución y auditoría

Se registró evolución en la cita 3:

```text
✓  Evolución registrada
```

Verificación directa en base:

```text
AUDIT [(3, None, 'Paciente completa sesion sin dolor.', 'cli_demo')]
```

La cita quedó en `ASISTIDA` y el trigger `trg_auditoria_evolucion` guardó el valor anterior (NULL) y el nuevo.

---

## 5. Cierre de tratamiento y eficacia

Se finalizó el tratamiento 1 (10 sesiones estimadas, 3 asistidas):

```text
✓  Tratamiento #1 cerrado
Eficacia calculada: 333.33%
```

Cálculo: `10 / 3 * 100 = 333.33%`. La eficacia puede superar el 100% si el paciente usó menos sesiones de las estimadas — el enunciado lo permite explícitamente.

---

## 6. Organigrama (CTE recursiva)

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

---

## 7. Cadena de referidos (CTE recursiva)

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

---

## 8. Adherencia (window functions)

Ejecutado después de insertar la cita del caso 3, para que el intervalo de Carlos Ruiz incluya esa fecha:

```text
Juan Perez    10.0   MEDIA (Seguimiento)
Carlos Ruiz   26.3   BAJA (Riesgo de Abandono)
Ana Beltrán   34.5   BAJA (Riesgo de Abandono)
```
