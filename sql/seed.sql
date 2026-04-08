/*
IA usada: ChatGPT
Prompt: "Necesito INSERTS para SQL con datos de prueba para las siguientes tablas"
*/

TRUNCATE auditoria_evolucion, pagos, citas, tratamientos, pacientes, personal
RESTART IDENTITY CASCADE;

INSERT INTO personal (id, nombre, rol, supervisor) VALUES
(1, 'Carlos Ramirez', 'Medico Senior', NULL),
(2, 'Ana Torres', 'Medico Senior', NULL),
(3, 'Luis Gomez', 'Medico Junior', 1),
(4, 'Maria Lopez', 'Medico Junior', 1),
(5, 'Jorge Castillo', 'Medico Junior', 2),
(6, 'Sofia Herrera', 'Tecnico', 3),
(7, 'Pedro Martinez', 'Tecnico', 3),
(8, 'Laura Diaz', 'Tecnico', 4),
(9, 'Andres Rojas', 'Fisioterapeuta', 2),
(10, 'Camila Vargas', 'Fisioterapeuta', 2),
(11, 'Diego Morales', 'Fisioterapeuta', 5);

INSERT INTO pacientes (id, nombre, fecha_nacimiento, contacto, referido_por) VALUES
(1, 'Juan Perez', '1985-03-15', 'juan.perez@email.com', NULL),
(2, 'Laura Sanchez', '1990-07-22', 'laura.s@email.com', 1),
(3, 'Carlos Medina', '1978-11-02', 'cmedina@email.com', NULL),
(4, 'Diana Rojas', '2000-01-30', 'diana.rojas@email.com', 2),
(5, 'Miguel Castro', '1965-09-18', 'miguel.c@email.com', NULL),
(6, 'Valentina Ruiz', '1995-05-10', 'val.ruiz@email.com', 3),
(7, 'Andres Silva', '1988-12-05', 'asilva@email.com', NULL),
(8, 'Paula Herrera', '2002-04-25', 'paula.h@email.com', 6);

INSERT INTO tratamientos (id, paciente_id, medico_id, diagnostico, sesiones_estimadas, estado, eficacia_porcentaje) VALUES
(1, 1, 1, 'Dolor lumbar crónico', 10, 'ACTIVO', NULL),
(2, 2, 3, 'Rehabilitación de rodilla', 15, 'ACTIVO', NULL),
(3, 3, 2, 'Terapia post-operatoria', 20, 'FINALIZADO', 85.50),
(4, 4, 4, 'Lesión muscular en pierna', 12, 'ACTIVO', NULL),
(5, 5, 1, 'Artritis leve', 8, 'FINALIZADO', 78.00),
(6, 6, 5, 'Recuperación de hombro', 14, 'ACTIVO', NULL),
(7, 7, 2, 'Dolor cervical', 9, 'FINALIZADO', 90.25),
(8, 8, 3, 'Rehabilitación post fractura', 18, 'ACTIVO', NULL);

INSERT INTO citas (id, tratamiento_id, fecha_hora, tipo_atencion, monto, pagado, asistida, nota_evolucion, personal_id) VALUES
(1, 1, '2026-01-10 09:00:00', 'Consulta', 50000, TRUE, TRUE, 'Paciente con leve mejoría', 1),
(2, 1, '2026-01-15 10:00:00', 'Terapia', 40000, FALSE, TRUE, 'Se mantiene tratamiento', 6),
(3, 2, '2026-02-01 11:00:00', 'Consulta', 60000, TRUE, TRUE, 'Evaluación inicial', 3),
(4, 2, '2026-02-05 09:30:00', 'Terapia', 45000, TRUE, TRUE, 'Buena evolución', 7),
(5, 3, '2026-01-20 08:00:00', 'Consulta', 55000, TRUE, TRUE, 'Post operatorio estable', 2),
(6, 3, '2026-01-25 08:30:00', 'Terapia', 50000, TRUE, TRUE, 'Recuperación favorable', 9),
(7, 4, '2026-03-01 14:00:00', 'Consulta', 48000, FALSE, FALSE, NULL, 4),
(8, 4, '2026-03-05 14:30:00', 'Terapia', 42000, FALSE, FALSE, NULL, 8),
(9, 5, '2026-01-12 07:30:00', 'Consulta', 52000, TRUE, TRUE, 'Dolor reducido', 1),
(10, 6, '2026-02-18 10:15:00', 'Terapia', 47000, FALSE, TRUE, 'Avance moderado', 10),
(11, 7, '2026-01-08 16:00:00', 'Consulta', 53000, TRUE, TRUE, 'Alta médica próxima', 2),
(12, 8, '2026-03-10 11:45:00', 'Terapia', 46000, FALSE, FALSE, NULL, 3);

SELECT setval(pg_get_serial_sequence('personal', 'id'), 11, TRUE);
SELECT setval(pg_get_serial_sequence('personal', 'equipo'), (SELECT MAX(equipo) FROM personal), TRUE);
SELECT setval(pg_get_serial_sequence('pacientes', 'id'), 8, TRUE);
SELECT setval(pg_get_serial_sequence('tratamientos', 'id'), 8, TRUE);
SELECT setval(pg_get_serial_sequence('citas', 'id'), 12, TRUE);
SELECT setval(pg_get_serial_sequence('pagos', 'id'), 1, FALSE);
SELECT setval(pg_get_serial_sequence('auditoria_evolucion', 'id'), 1, FALSE);
