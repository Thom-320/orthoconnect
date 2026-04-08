# Manual de Usuario — OrthoConnect CLI

## Inicio

Con la base cargada, ejecutar:

```bash
PYTHONPATH=. python -m src.main
```

Al arrancar se pregunta el modo (Demo o PostgreSQL) y el nombre del operador. Para la sustentación usar **PostgreSQL**. El nombre del operador queda registrado en auditoría y pagos.

Para obtener los mismos IDs del ejemplo del profesor, ejecutar primero `make reset-db`.

## Menú principal

```
1. Módulo Administrativo
2. Módulo Médico
3. Módulo de Consultas
4. Módulo Gerencial
5. Salir
```

## Módulo Administrativo

**Registrar paciente** — pide nombre, fecha de nacimiento, contacto y si fue referido. Si fue referido, muestra la lista para elegir el ID del referidor.

**Abrir tratamiento** — asocia un paciente con un médico, diagnóstico y número de sesiones estimadas. El tratamiento queda en `ACTIVO`.

**Agendar cita** — pide tratamiento, fecha/hora, monto, tipo de atención y profesional. Si el paciente tiene dos o más citas anteriores sin pagar, PostgreSQL lanza un error y la app lo muestra como regla de negocio violada.

**Registrar pago** — pide el `tratamiento_id` e invoca `fn_aplicar_pago()`, que salda la cita pendiente más antigua. Devuelve pago ID, cita ID, fecha, concepto y monto. Si no hay deudas, muestra el mensaje correspondiente sin cerrarse.

## Módulo Médico

**Registrar evolución** — pide `cita_id` y nota. Marca la cita como `ASISTIDA` y dispara el trigger de auditoría si ya había una nota anterior.

**Finalizar tratamiento** — cambia el estado a `FINALIZADO`. El trigger calcula la eficacia (`sesiones_estimadas / sesiones_asistidas * 100`) y la guarda en la base.

## Módulo de Consultas

- **Lista de pacientes** — muestra ID, nombre, contacto y referidor.
- **Deudas de paciente** — citas sin pagar con fecha, tipo, monto y diagnóstico.
- **Historial clínico** — por tratamiento y cita, incluyendo nota de evolución y eficacia si ya fue calculada.
- **Tratamientos por paciente** — resumen con estado, citas totales, asistidas y eficacia.

## Módulo Gerencial

- **Organigrama** — jerarquía completa de empleados usando `v_organigrama`.
- **Adherencia** — promedio de días entre citas por paciente y clasificación ALTA / MEDIA / BAJA.
- **Cadena de referidos** — árbol de paciente → referido usando `v_cadena_referidos`.
- **Eficacia** — resumen de tratamientos con sesiones estimadas, asistidas y porcentaje de eficacia.

## Manejo de errores

La app captura excepciones de PostgreSQL y las traduce a mensajes entendibles. Nunca colapsa por un error de negocio — muestra el mensaje y vuelve al menú.
