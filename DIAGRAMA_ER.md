# Diagrama ER — OrthoConnect

## Vista general

El modelo está organizado alrededor del paciente, sus tratamientos, las citas ejecutadas dentro de cada tratamiento, los pagos registrados y la auditoría clínica.

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

- `paciente` se autorrelaciona para soportar la cadena de referidos pedida en el parcial.
- `empleado` se autorrelaciona para representar el árbol de mando.
- `pago` es una entidad independiente para cumplir la rúbrica de modelado y dejar trazabilidad financiera.
- `cita.estado_asistencia` separa el hecho de haber asistido del hecho de haber pagado.
- `tratamiento.eficacia_porcentaje` se calcula por trigger al finalizar el tratamiento.

## Cardinalidades principales

- Un **médico senior** puede supervisar varios juniors.
- Un **médico junior** puede supervisar varios técnicos o fisioterapeutas.
- Un **paciente** puede tener varios tratamientos.
- Un **tratamiento** puede tener varias citas.
- Un **tratamiento** puede registrar varios pagos.
- Una **cita** puede generar múltiples registros de auditoría si la nota se edita varias veces.

## Reglas importantes reflejadas en el modelo

- Máximo una deuda pendiente efectiva antes de agendar una nueva cita; con dos anteriores sin pagar, el trigger bloquea.
- La eficacia solo considera citas `ASISTIDA`.
- Cada edición de evolución deja rastro de auditoría con `OLD` y `NEW`.
