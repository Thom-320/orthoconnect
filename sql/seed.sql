-- Datos de prueba OrthoConnect
-- Ejecutar despues de schema.sql

TRUNCATE pago, auditoria_evolucion, cita, tratamiento, paciente, empleado
RESTART IDENTITY CASCADE;

INSERT INTO empleado (nombre_completo, rol, especialidad, supervisor_id) VALUES
    ('Dr. Gregory House', 'MEDICO_SENIOR', 'Ortopedia Senior', NULL),
    ('Dr. Shaun Murphy', 'MEDICO_JUNIOR', 'Ortopedia Junior', 1),
    ('Lic. Wilson', 'FISIOTERAPEUTA', 'Fisioterapia', 2),
    ('Dra. Meredith Grey', 'MEDICO_SENIOR', 'Cirugia Ortopedica', NULL),
    ('Dra. Lexie Grey', 'MEDICO_JUNIOR', 'Ortopedia General', 4),
    ('Dr. George O''Malley', 'MEDICO_JUNIOR', 'Traumatologia', 4),
    ('Dr. Derek Shepherd', 'MEDICO_SENIOR', 'Neuro-Ortopedia', NULL),
    ('Dr. Jackson Avery', 'MEDICO_JUNIOR', 'Rehabilitacion', 7),
    ('Ft. Jo Wilson', 'FISIOTERAPEUTA', 'Fisioterapia Deportiva', 8),
    ('Ft. April Kepner', 'FISIOTERAPEUTA', 'Recuperacion Funcional', 8),
    ('Ft. Ben Warren', 'TECNICO', 'Terapia Ocupacional', 8);

INSERT INTO paciente (nombre_completo, fecha_nacimiento, contacto, referido_por_paciente_id) VALUES
    ('Juan Perez', '1990-05-15', '555-0101', NULL),
    ('Maria Lopez', '1985-10-20', '555-0202', 1),
    ('Pedro Gomez', '1992-01-10', '555-0303', 2),
    ('Carlos Ruiz', '1978-03-12', '3001112233', NULL),
    ('Ana Beltran', '1995-07-25', '3004445566', 4),
    ('Luis Diaz', '2000-11-02', '3159998877', 5),
    ('Sofia Vergara', '1982-05-30', '3203332211', 4),
    ('James Rodriguez', '1991-07-12', '3104443322', 6);

INSERT INTO tratamiento (paciente_id, medico_empleado_id, diagnostico, sesiones_estimadas, estado, eficacia_porcentaje) VALUES
    (1, 1, 'Fractura de femur', 10, 'ACTIVO', NULL),
    (2, 4, 'Reconstruccion de LCA', 12, 'FINALIZADO', 400.00),
    (4, 7, 'Fractura', 3, 'ACTIVO', NULL),
    (5, 5, 'Esguince de tobillo', 6, 'ACTIVO', NULL),
    (6, 8, 'Lesion meniscal', 5, 'ACTIVO', NULL);

INSERT INTO cita (
    tratamiento_id,
    fecha_hora,
    tipo_atencion,
    monto,
    pagado,
    estado_asistencia,
    nota_evolucion,
    profesional_empleado_id
) VALUES
    (1, '2026-03-01 08:00', 'Consulta inicial', 80000, FALSE, 'PROGRAMADA', NULL, 1),
    (1, '2026-03-05 09:00', 'Fisioterapia 1', 50000, TRUE, 'ASISTIDA', 'Buena evolucion', 3),
    (1, '2026-03-22 10:00', 'Sesion control', 50000, FALSE, 'PROGRAMADA', NULL, 3),

    (2, '2026-01-05 08:00', 'Fisioterapia', 60000, TRUE, 'ASISTIDA', 'Paciente inicia fase de movilidad pasiva. Dolor 4/10.', 9),
    (2, '2026-01-08 08:00', 'Fisioterapia', 60000, TRUE, 'ASISTIDA', 'Se observa edema leve. Se recomienda hielo local.', 9),
    (2, '2026-01-12 08:00', 'Fisioterapia', 60000, TRUE, 'ASISTIDA', NULL, 9),

    (3, '2026-01-10 10:00', 'Consulta', 70000, TRUE, 'ASISTIDA', NULL, 7),
    (3, '2026-02-15 10:00', 'Control', 50000, TRUE, 'ASISTIDA', NULL, 7),
    (3, '2026-03-20 10:00', 'Fisioterapia', 50000, TRUE, 'ASISTIDA', NULL, 9),

    (4, '2026-01-01 09:00', 'Inicial', 40000, TRUE, 'ASISTIDA', NULL, 5),
    (4, '2026-02-10 09:00', 'Control', 40000, TRUE, 'ASISTIDA', NULL, 5),

    (5, '2026-01-03 07:30', 'Valoracion', 45000, TRUE, 'ASISTIDA', NULL, 8),
    (5, '2026-01-10 07:30', 'Terapia fisica', 45000, TRUE, 'ASISTIDA', NULL, 9),
    (5, '2026-01-17 07:30', 'Terapia fisica', 45000, TRUE, 'ASISTIDA', NULL, 10);

INSERT INTO pago (tratamiento_id, cita_id_saldada, fecha_pago, monto, usuario_registro) VALUES
    (1, 2, '2026-03-05 09:40', 50000, 'seed'),
    (2, 4, '2026-01-05 08:45', 60000, 'seed'),
    (2, 5, '2026-01-08 08:45', 60000, 'seed'),
    (2, 6, '2026-01-12 08:45', 60000, 'seed'),
    (3, 7, '2026-01-10 10:30', 70000, 'seed'),
    (3, 8, '2026-02-15 10:30', 50000, 'seed'),
    (3, 9, '2026-03-20 10:30', 50000, 'seed'),
    (4, 10, '2026-01-01 09:30', 40000, 'seed'),
    (4, 11, '2026-02-10 09:30', 40000, 'seed'),
    (5, 12, '2026-01-03 08:00', 45000, 'seed'),
    (5, 13, '2026-01-10 08:00', 45000, 'seed'),
    (5, 14, '2026-01-17 08:00', 45000, 'seed');

INSERT INTO auditoria_evolucion (
    cita_id,
    nota_anterior,
    nota_nueva,
    usuario_editor,
    fecha_edicion
) VALUES
    (2, NULL, 'Buena evolucion', 'seed', '2026-03-05 09:05');

SELECT setval(pg_get_serial_sequence('empleado', 'empleado_id'), COALESCE((SELECT MAX(empleado_id) FROM empleado), 1));
SELECT setval(pg_get_serial_sequence('paciente', 'paciente_id'), COALESCE((SELECT MAX(paciente_id) FROM paciente), 1));
SELECT setval(pg_get_serial_sequence('tratamiento', 'tratamiento_id'), COALESCE((SELECT MAX(tratamiento_id) FROM tratamiento), 1));
SELECT setval(pg_get_serial_sequence('cita', 'cita_id'), COALESCE((SELECT MAX(cita_id) FROM cita), 1));
SELECT setval(pg_get_serial_sequence('pago', 'pago_id'), COALESCE((SELECT MAX(pago_id) FROM pago), 1));
SELECT setval(pg_get_serial_sequence('auditoria_evolucion', 'auditoria_id'), COALESCE((SELECT MAX(auditoria_id) FROM auditoria_evolucion), 1));
