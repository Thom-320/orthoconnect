-- Datos de prueba OrthoConnect
-- Ejecutar despues de schema.sql
-- Estos datos son sinteticos.
-- Se construyeron a partir de la narrativa del parcial y del bloque de ejemplo
-- incluido por el profesor en Parcial2.docx, intentando reproducir lo mas fielmente
-- posible los nombres, jerarquias, IDs y escenarios de demostracion.

TRUNCATE pago, auditoria_evolucion, cita, tratamiento, paciente, empleado
RESTART IDENTITY CASCADE;

INSERT INTO empleado (empleado_id, nombre_completo, rol, especialidad, supervisor_id) VALUES
    (1, 'Dr. Gregory House', 'MEDICO_SENIOR', 'Ortopedia Senior', NULL),
    (2, 'Dr. Shaun Murphy', 'MEDICO_JUNIOR', 'Ortopedia Junior', 1),
    (3, 'Lic. Wilson', 'FISIOTERAPEUTA', 'Fisioterapia', 2),
    (4, 'Dra. Meredith Grey', 'MEDICO_SENIOR', 'Cirugía Ortopédica', NULL),
    (5, 'Dra. Lexie Grey', 'MEDICO_JUNIOR', 'Ortopedia General', 4),
    (6, 'Dr. George O''Malley', 'MEDICO_JUNIOR', 'Traumatología', 4),
    (7, 'Dr. Derek Shepherd', 'MEDICO_SENIOR', 'Neuro-Ortopedia', NULL),
    (8, 'Dr. Jackson Avery', 'MEDICO_JUNIOR', 'Rehabilitación', 7),
    (9, 'Ft. Jo Wilson', 'FISIOTERAPEUTA', 'Fisioterapia Deportiva', 8),
    (10, 'Ft. April Kepner', 'FISIOTERAPEUTA', 'Recuperación Funcional', 8),
    (11, 'Ft. Ben Warren', 'TECNICO', 'Terapia Ocupacional', 8);

INSERT INTO paciente (paciente_id, nombre_completo, fecha_nacimiento, contacto, referido_por_paciente_id) VALUES
    (1, 'Juan Perez', '1990-05-15', '555-0101', NULL),
    (2, 'Maria Lopez', '1985-10-20', '555-0202', 1),
    (3, 'Pedro Gomez', '1992-01-10', '555-0303', 2),
    (4, 'Carlos Ruiz', '1978-03-12', '3001112233', NULL),
    (5, 'Ana Beltrán', '1995-07-25', '3004445566', 4),
    (6, 'Luis Díaz', '2000-11-02', '3159998877', 5),
    (7, 'Sofía Vergara', '1982-05-30', '3203332211', 4),
    (8, 'James Rodriguez', '1991-07-12', '3104443322', 6);

INSERT INTO tratamiento (
    tratamiento_id,
    paciente_id,
    medico_empleado_id,
    diagnostico,
    sesiones_estimadas,
    estado,
    eficacia_porcentaje
) VALUES
    (1, 1, 1, 'Fractura de fémur', 10, 'ACTIVO', NULL),
    (2, 2, 2, 'Tendinitis rotuliana', 5, 'ACTIVO', NULL),
    (3, 4, 4, 'Reconstrucción de LCA', 12, 'FINALIZADO', 400.00),
    (4, 5, 5, 'Esguince', 6, 'ACTIVO', NULL),
    (5, 3, 6, 'Luxación de hombro', 4, 'ACTIVO', NULL),
    (6, 6, 8, 'Recuperación funcional', 5, 'ACTIVO', NULL),
    (7, 4, 7, 'Fractura', 3, 'ACTIVO', NULL);

INSERT INTO cita (
    cita_id,
    tratamiento_id,
    fecha_hora,
    tipo_atencion,
    monto,
    pagado,
    estado_asistencia,
    nota_evolucion,
    profesional_empleado_id
) VALUES
    (1, 1, '2026-03-01 08:00', 'Consulta inicial', 80000, FALSE, 'ASISTIDA', NULL, 1),
    (2, 1, '2026-03-05 09:00', 'Fisioterapia 1', 50000, TRUE, 'ASISTIDA', 'Buena evolución', 3),
    (3, 1, '2026-03-21 08:00', 'Sesión Control', 50000, FALSE, 'ASISTIDA', NULL, 3),

    (4, 3, '2026-01-05 10:00', 'Fisioterapia', 60000, TRUE, 'ASISTIDA', 'Paciente inicia fase de movilidad pasiva. Dolor 4/10.', 9),
    (5, 3, '2026-01-08 10:00', 'Fisioterapia', 60000, TRUE, 'ASISTIDA', 'Se observa edema leve. Se recomienda hielo local.', 9),
    (6, 3, '2026-01-12 10:00', 'Fisioterapia', 60000, TRUE, 'ASISTIDA', NULL, 9),

    (7, 4, '2026-01-01 09:00', 'Inicial', 40000, TRUE, 'ASISTIDA', NULL, 5),
    (8, 4, '2026-02-04 21:00', 'Control', 40000, TRUE, 'ASISTIDA', NULL, 5),

    (9, 2, '2026-02-18 08:00', 'Valoración', 45000, FALSE, 'PROGRAMADA', NULL, 2),
    (10, 5, '2026-02-02 11:00', 'Valoración', 30000, TRUE, 'ASISTIDA', NULL, 6),
    (11, 6, '2026-02-20 07:30', 'Terapia física', 45000, TRUE, 'ASISTIDA', NULL, 8);

INSERT INTO pago (pago_id, tratamiento_id, cita_id_saldada, fecha_pago, monto, usuario_registro) VALUES
    (1, 1, 2, '2026-03-05 09:40', 50000, 'seed'),
    (2, 3, 4, '2026-01-05 08:45', 60000, 'seed'),
    (3, 3, 5, '2026-01-08 08:45', 60000, 'seed'),
    (4, 3, 6, '2026-01-12 10:45', 60000, 'seed'),
    (5, 4, 7, '2026-01-01 09:30', 40000, 'seed'),
    (6, 4, 8, '2026-02-04 21:30', 40000, 'seed'),
    (7, 5, 10, '2026-02-02 11:30', 30000, 'seed'),
    (8, 6, 11, '2026-02-20 08:00', 45000, 'seed');

INSERT INTO auditoria_evolucion (
    auditoria_id,
    cita_id,
    nota_anterior,
    nota_nueva,
    usuario_editor,
    fecha_edicion
) VALUES
    (1, 2, NULL, 'Buena evolución', 'seed', '2026-03-05 09:05');

SELECT setval(pg_get_serial_sequence('empleado', 'empleado_id'), 11, TRUE);
SELECT setval(pg_get_serial_sequence('paciente', 'paciente_id'), 8, TRUE);
SELECT setval(pg_get_serial_sequence('tratamiento', 'tratamiento_id'), 7, TRUE);
SELECT setval(pg_get_serial_sequence('cita', 'cita_id'), 12, TRUE);
SELECT setval(pg_get_serial_sequence('pago', 'pago_id'), 12, TRUE);
SELECT setval(pg_get_serial_sequence('auditoria_evolucion', 'auditoria_id'), 1, TRUE);
