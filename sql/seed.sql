-- Datos de prueba OrthoConnect (ejecutar después de schema.sql)

TRUNCATE auditoria_evolucion, cita, tratamiento, paciente, empleado RESTART IDENTITY CASCADE;

INSERT INTO empleado (nombre_completo, rol, especialidad, supervisor_id) VALUES
    ('Dr. Gregory House', 'MEDICO_SENIOR', 'Ortopedia Senior', NULL),
    ('Dr. Shaun Murphy', 'MEDICO_JUNIOR', 'Ortopedia Junior', 1),
    ('Lic. Wilson', 'FISIOTERAPEUTA', 'Fisioterapia', 2),
    ('Dra. Meredith Grey', 'MEDICO_SENIOR', 'Cirugía Ortopédica', NULL),
    ('Dra. Lexie Grey', 'MEDICO_JUNIOR', 'Ortopedia General', 4),
    ('Dr. George O''Malley', 'MEDICO_JUNIOR', 'Traumatología', 4),
    ('Dr. Derek Shepherd', 'MEDICO_SENIOR', 'Neuro-Ortopedia', NULL),
    ('Dr. Jackson Avery', 'MEDICO_JUNIOR', 'Rehabilitación', 7),
    ('Ft. Jo Wilson', 'FISIOTERAPEUTA', 'Fisioterapia Deportiva', 8),
    ('Ft. April Kepner', 'FISIOTERAPEUTA', 'Recuperación Funcional', 8),
    ('Ft. Ben Warren', 'TECNICO', 'Terapia Ocupacional', 8);

INSERT INTO paciente (nombre_completo, fecha_nacimiento, contacto, referido_por_paciente_id) VALUES
    ('Juan Perez', '1990-05-15', '555-0101', NULL),
    ('Maria Lopez', '1985-10-20', '555-0202', 1),
    ('Pedro Gomez', '1992-01-10', '555-0303', 2),
    ('Carlos Ruiz', '1978-03-12', '3001112233', NULL),
    ('Ana Beltrán', '1995-07-25', '3004445566', 4),
    ('Luis Díaz', '2000-11-02', '3159998877', 5),
    ('Sofía Vergara', '1982-05-30', '3203332211', 4),
    ('James Rodriguez', '1991-07-12', '3104443322', 6);

-- Tratamiento 1: Juan Perez, House, activo, 3 citas (2 pendientes de pago para probar morosidad)
INSERT INTO tratamiento (paciente_id, medico_empleado_id, diagnostico, sesiones_estimadas, estado)
VALUES (1, 1, 'Fractura de fémur', 10, 'ACTIVO');

INSERT INTO cita (tratamiento_id, fecha_hora, tipo_atencion, monto, pagado, nota_evolucion, profesional_empleado_id)
VALUES
    (1, '2026-03-01 08:00', 'Consulta inicial', 80000, FALSE, NULL, 1),
    (1, '2026-03-05 09:00', 'Fisioterapia 1', 50000, TRUE, 'Buena evolución', 3),
    (1, '2026-03-22 00:00', 'Sesión Control', 50000, FALSE, NULL, 3);

-- Tratamiento finalizado: 12 estimadas, 3 citas reales -> 400% eficacia
INSERT INTO tratamiento (paciente_id, medico_empleado_id, diagnostico, sesiones_estimadas, estado, eficacia_porcentaje)
VALUES (2, 4, 'Reconstrucción de LCA', 12, 'FINALIZADO', 400.00);

-- Tres citas históricas; deben ir pagadas al insertar en lote (el trigger limita 2 pendientes por paciente).
INSERT INTO cita (tratamiento_id, fecha_hora, tipo_atencion, monto, pagado, nota_evolucion, profesional_empleado_id)
VALUES
    (2, '2026-01-05 08:00', 'Fisioterapia', 60000, TRUE, 'Paciente inicia fase de movilidad pasiva. Dolor 4/10.', 9),
    (2, '2026-01-08 08:00', 'Fisioterapia', 60000, TRUE, 'Se observa edema leve. Se recomienda hielo local.', 9),
    (2, '2026-01-12 08:00', 'Fisioterapia', 60000, TRUE, NULL, 9);

-- Carlos Ruiz: tratamiento activo con varias citas para adherencia BAJA
INSERT INTO tratamiento (paciente_id, medico_empleado_id, diagnostico, sesiones_estimadas, estado)
VALUES (4, 7, 'Fractura', 3, 'ACTIVO');

INSERT INTO cita (tratamiento_id, fecha_hora, tipo_atencion, monto, pagado, nota_evolucion)
VALUES
    (3, '2026-01-10 10:00', 'Consulta', 70000, TRUE, NULL),
    (3, '2026-02-15 10:00', 'Control', 50000, TRUE, NULL),
    (3, '2026-03-20 10:00', 'Fisioterapia', 50000, TRUE, NULL);

-- Ana Beltrán: otro paciente para adherencia
INSERT INTO tratamiento (paciente_id, medico_empleado_id, diagnostico, sesiones_estimadas, estado)
VALUES (5, 5, 'Esguince', 6, 'ACTIVO');

INSERT INTO cita (tratamiento_id, fecha_hora, tipo_atencion, monto, pagado)
VALUES
    (4, '2026-01-01 09:00', 'Inicial', 40000, TRUE),
    (4, '2026-02-10 09:00', 'Control', 40000, TRUE);

-- Juan Perez: segunda racha de citas vía otro tratamiento no — adherencia usa todas las citas del paciente
-- Añadimos más citas al tratamiento 1 para intervalos ~10 días entre algunas (ya hay 3 citas)

-- Ajuste: citas de Juan mezcladas para promedio ~10: ya tenemos mar 1, mar 5 (4d), mar 22 (17d) -> avg (4+17)/2 = 10.5 -> MEDIA

SELECT setval(pg_get_serial_sequence('empleado', 'empleado_id'), (SELECT COALESCE(MAX(empleado_id), 1) FROM empleado));
SELECT setval(pg_get_serial_sequence('paciente', 'paciente_id'), (SELECT COALESCE(MAX(paciente_id), 1) FROM paciente));
SELECT setval(pg_get_serial_sequence('tratamiento', 'tratamiento_id'), (SELECT COALESCE(MAX(tratamiento_id), 1) FROM tratamiento));
SELECT setval(pg_get_serial_sequence('cita', 'cita_id'), (SELECT COALESCE(MAX(cita_id), 1) FROM cita));
