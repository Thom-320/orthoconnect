# Diagrama ER — OrthoConnect

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

- `empleado` se autorrelaciona (`supervisor_id`) para representar el árbol de mando del enunciado.
- `paciente` se autorrelaciona (`referido_por_paciente_id`) para la cadena de referidos.
- `cita` tiene dos campos separados: `pagado` para cobranza y `estado_asistencia` para evidencia clínica. No son lo mismo — una cita puede estar pagada y no asistida, o al revés.
- `pago` es una entidad propia para dejar trazabilidad de cada transacción.
- `eficacia_porcentaje` se guarda en `tratamiento` porque el trigger la calcula una sola vez al cierre; no tiene sentido recalcularla cada vez.
