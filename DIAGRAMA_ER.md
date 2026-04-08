# Diagrama ER — OrthoConnect

## Vista general

El centro del modelo es el paciente. Desde ahí salen los tratamientos, las citas, los pagos y la auditoría.

```mermaid
erDiagram
    EMPLEADO ||--o{ EMPLEADO : supervisa
    EMPLEADO ||--o{ TRATAMIENTO : trata
    EMPLEADO ||--o{ CITA : atiende

    PACIENTE ||--o{ PACIENTE : refiere
    PACIENTE ||--o{ TRATAMIENTO : tiene

    TRATAMIENTO ||--o{ CITA : agenda
    TRATAMIENTO ||--o{ PAGO : recibe

    CITA ||--o{ AUDITORIA_EVOLUCION : audita
    CITA ||--|| PAGO : salda

    EMPLEADO {
        int empleado_id PK
        string nombre_completo
        string rol
        string especialidad
        int supervisor_id FK
    }

    PACIENTE {
        int paciente_id PK
        string nombre_completo
        date fecha_nacimiento
        string contacto
        int referido_por_paciente_id FK
    }

    TRATAMIENTO {
        int tratamiento_id PK
        int paciente_id FK
        int medico_empleado_id FK
        string diagnostico
        int sesiones_estimadas
        string estado
        decimal eficacia_porcentaje
    }

    CITA {
        int cita_id PK
        int tratamiento_id FK
        datetime fecha_hora
        string tipo_atencion
        decimal monto
        boolean pagado
        string estado_asistencia
        text nota_evolucion
        int profesional_empleado_id FK
    }

    PAGO {
        int pago_id PK
        int tratamiento_id FK
        int cita_id_saldada FK
        datetime fecha_pago
        decimal monto
        string usuario_registro
    }

    AUDITORIA_EVOLUCION {
        int auditoria_id PK
        int cita_id FK
        text nota_anterior
        text nota_nueva
        string usuario_editor
        datetime fecha_edicion
    }
```

## Decisiones de modelado

- `paciente` se autorrelaciona para manejar la cadena de referidos.
- `empleado` se autorrelaciona para representar el árbol de mando.
- `pago` quedó como entidad aparte para no reducir todo a un `pagado = true/false`.
- `estado_asistencia` quedó separado de `pagado` porque no significan lo mismo.
- `eficacia_porcentaje` se guarda en `tratamiento` porque se calcula al cierre.

## Cardinalidades principales

- Un médico senior puede supervisar varios juniors.
- Un médico junior puede supervisar varios técnicos o fisioterapeutas.
- Un paciente puede tener varios tratamientos.
- Un tratamiento puede tener varias citas.
- Un tratamiento puede tener varios pagos.
- Una cita puede tener varios registros en auditoría si la nota se edita más de una vez.

## Reglas reflejadas en el modelo

- Si un paciente ya tiene dos citas anteriores sin pagar, no se le puede agendar otra.
- La eficacia solo cuenta citas `ASISTIDA`.
- Cada cambio en la evolución deja rastro con valor anterior, valor nuevo, usuario y fecha.

En resumen, el diagrama se pensó para cubrir lo que pide el enunciado sin dejar pagos, jerarquía o referidos resueltos “a medias”.
