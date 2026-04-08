-- OrthoConnect: esquema, funciones, triggers y vistas
-- Entrega oficial del Proyecto Integrador (Parcial 2)

DROP TRIGGER IF EXISTS trg_auditoria_evolucion ON cita;
DROP TRIGGER IF EXISTS trg_morosidad_agenda ON cita;
DROP TRIGGER IF EXISTS trg_eficacia_tratamiento ON tratamiento;

DROP VIEW IF EXISTS v_reporte_adherencia;
DROP VIEW IF EXISTS v_adherencia_detalle;
DROP VIEW IF EXISTS v_cadena_referidos;
DROP VIEW IF EXISTS v_organigrama;

DROP FUNCTION IF EXISTS fn_aplicar_pago(INTEGER);
DROP FUNCTION IF EXISTS fn_check_morosidad();
DROP FUNCTION IF EXISTS fn_calcular_eficacia_tratamiento();
DROP FUNCTION IF EXISTS fn_auditoria_evolucion();

DROP TABLE IF EXISTS pago;
DROP TABLE IF EXISTS auditoria_evolucion;
DROP TABLE IF EXISTS cita;
DROP TABLE IF EXISTS tratamiento;
DROP TABLE IF EXISTS paciente;
DROP TABLE IF EXISTS empleado;

CREATE TABLE empleado (
    empleado_id SERIAL PRIMARY KEY,
    nombre_completo VARCHAR(200) NOT NULL,
    rol VARCHAR(30) NOT NULL
        CHECK (rol IN ('MEDICO_SENIOR', 'MEDICO_JUNIOR', 'TECNICO', 'FISIOTERAPEUTA')),
    especialidad VARCHAR(150) NOT NULL,
    supervisor_id INTEGER REFERENCES empleado (empleado_id) ON DELETE SET NULL
);

CREATE TABLE paciente (
    paciente_id SERIAL PRIMARY KEY,
    nombre_completo VARCHAR(200) NOT NULL,
    fecha_nacimiento DATE NOT NULL,
    contacto VARCHAR(80) NOT NULL,
    referido_por_paciente_id INTEGER REFERENCES paciente (paciente_id) ON DELETE SET NULL
);

CREATE TABLE tratamiento (
    tratamiento_id SERIAL PRIMARY KEY,
    paciente_id INTEGER NOT NULL REFERENCES paciente (paciente_id) ON DELETE CASCADE,
    medico_empleado_id INTEGER NOT NULL REFERENCES empleado (empleado_id) ON DELETE RESTRICT,
    diagnostico TEXT NOT NULL,
    sesiones_estimadas INTEGER NOT NULL CHECK (sesiones_estimadas > 0),
    estado VARCHAR(20) NOT NULL DEFAULT 'ACTIVO'
        CHECK (estado IN ('ACTIVO', 'FINALIZADO')),
    eficacia_porcentaje NUMERIC(10, 2)
);

CREATE TABLE cita (
    cita_id SERIAL PRIMARY KEY,
    tratamiento_id INTEGER NOT NULL REFERENCES tratamiento (tratamiento_id) ON DELETE CASCADE,
    fecha_hora TIMESTAMP NOT NULL,
    tipo_atencion VARCHAR(120) NOT NULL,
    monto NUMERIC(12, 2) NOT NULL CHECK (monto >= 0),
    pagado BOOLEAN NOT NULL DEFAULT FALSE,
    estado_asistencia VARCHAR(20) NOT NULL DEFAULT 'PROGRAMADA'
        CHECK (estado_asistencia IN ('PROGRAMADA', 'ASISTIDA', 'NO_ASISTIO', 'CANCELADA')),
    nota_evolucion TEXT,
    profesional_empleado_id INTEGER REFERENCES empleado (empleado_id) ON DELETE SET NULL
);

CREATE TABLE pago (
    pago_id SERIAL PRIMARY KEY,
    tratamiento_id INTEGER NOT NULL REFERENCES tratamiento (tratamiento_id) ON DELETE CASCADE,
    cita_id_saldada INTEGER NOT NULL REFERENCES cita (cita_id) ON DELETE RESTRICT,
    fecha_pago TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    monto NUMERIC(12, 2) NOT NULL CHECK (monto >= 0),
    usuario_registro VARCHAR(200) NOT NULL
);

CREATE TABLE auditoria_evolucion (
    auditoria_id SERIAL PRIMARY KEY,
    cita_id INTEGER NOT NULL REFERENCES cita (cita_id) ON DELETE CASCADE,
    nota_anterior TEXT,
    nota_nueva TEXT,
    usuario_editor VARCHAR(200) NOT NULL,
    fecha_edicion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_empleado_supervisor ON empleado (supervisor_id);
CREATE INDEX idx_paciente_referido ON paciente (referido_por_paciente_id);
CREATE INDEX idx_tratamiento_paciente ON tratamiento (paciente_id);
CREATE INDEX idx_tratamiento_estado ON tratamiento (estado);
CREATE INDEX idx_cita_tratamiento_fecha ON cita (tratamiento_id, fecha_hora);
CREATE INDEX idx_cita_pendiente ON cita (pagado, fecha_hora);
CREATE INDEX idx_pago_tratamiento ON pago (tratamiento_id, fecha_pago);
CREATE INDEX idx_auditoria_cita ON auditoria_evolucion (cita_id, fecha_edicion);

CREATE OR REPLACE FUNCTION fn_check_morosidad()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_paciente_id INTEGER;
    v_pendientes_anteriores INTEGER;
BEGIN
    SELECT t.paciente_id
    INTO v_paciente_id
    FROM tratamiento t
    WHERE t.tratamiento_id = NEW.tratamiento_id;

    IF v_paciente_id IS NULL THEN
        RAISE EXCEPTION 'BLOQUEO: El tratamiento indicado no existe.'
            USING ERRCODE = 'P0001';
    END IF;

    SELECT COUNT(*)
    INTO v_pendientes_anteriores
    FROM cita c
    JOIN tratamiento t ON t.tratamiento_id = c.tratamiento_id
    WHERE t.paciente_id = v_paciente_id
      AND c.pagado = FALSE
      AND c.fecha_hora < NEW.fecha_hora;

    IF v_pendientes_anteriores >= 2 THEN
        RAISE EXCEPTION
            'BLOQUEO: El paciente tiene % citas anteriores pendientes. Debe ponerse al día.',
            v_pendientes_anteriores
            USING ERRCODE = 'P0001';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_morosidad_agenda
    BEFORE INSERT ON cita
    FOR EACH ROW
    EXECUTE PROCEDURE fn_check_morosidad();

CREATE OR REPLACE FUNCTION fn_calcular_eficacia_tratamiento()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_sesiones_asistidas INTEGER;
BEGIN
    IF NEW.estado = 'FINALIZADO' AND OLD.estado IS DISTINCT FROM 'FINALIZADO' THEN
        SELECT COUNT(*)
        INTO v_sesiones_asistidas
        FROM cita
        WHERE tratamiento_id = NEW.tratamiento_id
          AND estado_asistencia = 'ASISTIDA';

        IF v_sesiones_asistidas = 0 THEN
            NEW.eficacia_porcentaje := NULL;
        ELSE
            NEW.eficacia_porcentaje := ROUND(
                (NEW.sesiones_estimadas::NUMERIC / v_sesiones_asistidas::NUMERIC) * 100,
                2
            );
        END IF;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_eficacia_tratamiento
    BEFORE UPDATE OF estado ON tratamiento
    FOR EACH ROW
    EXECUTE PROCEDURE fn_calcular_eficacia_tratamiento();

CREATE OR REPLACE FUNCTION fn_auditoria_evolucion()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_user TEXT;
BEGIN
    IF OLD.nota_evolucion IS DISTINCT FROM NEW.nota_evolucion THEN
        v_user := current_setting('application_name', true);
        IF v_user IS NULL OR v_user = '' THEN
            v_user := 'desconocido';
        END IF;

        INSERT INTO auditoria_evolucion (
            cita_id,
            nota_anterior,
            nota_nueva,
            usuario_editor
        )
        VALUES (
            OLD.cita_id,
            OLD.nota_evolucion,
            NEW.nota_evolucion,
            v_user
        );
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_auditoria_evolucion
    AFTER UPDATE OF nota_evolucion ON cita
    FOR EACH ROW
    EXECUTE PROCEDURE fn_auditoria_evolucion();

CREATE OR REPLACE FUNCTION fn_aplicar_pago(p_tratamiento_id INTEGER)
RETURNS TABLE (
    pago_id_registrado INTEGER,
    cita_id_pagada INTEGER,
    fecha_hora_cita TIMESTAMP,
    tipo_atencion_pago VARCHAR(120),
    monto_pagado NUMERIC(12, 2)
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_cita RECORD;
    v_pago_id INTEGER;
    v_user TEXT;
BEGIN
    SELECT
        c.cita_id,
        c.fecha_hora,
        c.tipo_atencion,
        c.monto
    INTO v_cita
    FROM cita c
    WHERE c.tratamiento_id = p_tratamiento_id
      AND c.pagado = FALSE
    ORDER BY c.fecha_hora ASC, c.cita_id ASC
    LIMIT 1
    FOR UPDATE OF c;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'INFO:NO_HAY_DEUDAS: No hay citas pendientes de pago para este tratamiento.'
            USING ERRCODE = 'P0001';
    END IF;

    v_user := current_setting('application_name', true);
    IF v_user IS NULL OR v_user = '' THEN
        v_user := 'desconocido';
    END IF;

    UPDATE cita
    SET pagado = TRUE
    WHERE cita_id = v_cita.cita_id;

    INSERT INTO pago (
        tratamiento_id,
        cita_id_saldada,
        fecha_pago,
        monto,
        usuario_registro
    )
    VALUES (
        p_tratamiento_id,
        v_cita.cita_id,
        CURRENT_TIMESTAMP,
        v_cita.monto,
        v_user
    )
    RETURNING pago_id INTO v_pago_id;

    RETURN QUERY
    SELECT
        v_pago_id,
        v_cita.cita_id,
        v_cita.fecha_hora,
        v_cita.tipo_atencion::VARCHAR(120),
        v_cita.monto::NUMERIC(12, 2);
END;
$$;

CREATE OR REPLACE VIEW v_organigrama AS
WITH RECURSIVE arbol AS (
    SELECT
        e.empleado_id,
        e.nombre_completo,
        e.rol,
        e.especialidad,
        e.supervisor_id,
        0 AS nivel,
        LPAD(e.empleado_id::TEXT, 6, '0') AS ruta_orden
    FROM empleado e
    WHERE e.rol = 'MEDICO_SENIOR'

    UNION ALL

    SELECT
        e.empleado_id,
        e.nombre_completo,
        e.rol,
        e.especialidad,
        e.supervisor_id,
        a.nivel + 1,
        a.ruta_orden || '.' || LPAD(e.empleado_id::TEXT, 6, '0') AS ruta_orden
    FROM empleado e
    JOIN arbol a ON e.supervisor_id = a.empleado_id
)
SELECT
    empleado_id,
    nombre_completo,
    rol,
    especialidad,
    supervisor_id,
    nivel,
    ruta_orden
FROM arbol;

CREATE OR REPLACE VIEW v_cadena_referidos AS
WITH RECURSIVE cadena AS (
    SELECT
        p.paciente_id,
        p.nombre_completo,
        p.referido_por_paciente_id,
        0 AS nivel,
        p.nombre_completo::TEXT AS cadena_texto
    FROM paciente p
    WHERE p.referido_por_paciente_id IS NULL

    UNION ALL

    SELECT
        p.paciente_id,
        p.nombre_completo,
        p.referido_por_paciente_id,
        c.nivel + 1,
        c.cadena_texto || ' -> ' || p.nombre_completo
    FROM paciente p
    JOIN cadena c ON p.referido_por_paciente_id = c.paciente_id
)
SELECT
    paciente_id,
    nombre_completo,
    referido_por_paciente_id,
    nivel,
    cadena_texto
FROM cadena;

CREATE OR REPLACE VIEW v_adherencia_detalle AS
WITH citas_paciente AS (
    SELECT
        p.paciente_id,
        p.nombre_completo,
        t.tratamiento_id,
        c.cita_id,
        c.fecha_hora,
        LAG(c.fecha_hora) OVER (
            PARTITION BY p.paciente_id
            ORDER BY c.fecha_hora
        ) AS fecha_previa
    FROM cita c
    JOIN tratamiento t ON t.tratamiento_id = c.tratamiento_id
    JOIN paciente p ON p.paciente_id = t.paciente_id
)
SELECT
    paciente_id,
    nombre_completo,
    tratamiento_id,
    cita_id,
    fecha_hora,
    fecha_previa,
    ROUND(EXTRACT(EPOCH FROM (fecha_hora - fecha_previa)) / 86400.0, 1) AS dias_desde_cita_previa
FROM citas_paciente
WHERE fecha_previa IS NOT NULL;

CREATE OR REPLACE VIEW v_reporte_adherencia AS
SELECT
    paciente_id,
    nombre_completo,
    ROUND(AVG(dias_desde_cita_previa)::NUMERIC, 1) AS promedio_dias_entre_citas,
    CASE
        WHEN ROUND(AVG(dias_desde_cita_previa)::NUMERIC, 1) <= 7 THEN 'ALTA (Ideal)'
        WHEN ROUND(AVG(dias_desde_cita_previa)::NUMERIC, 1) <= 15 THEN 'MEDIA (Seguimiento)'
        ELSE 'BAJA (Riesgo de Abandono)'
    END AS estado_adherencia
FROM v_adherencia_detalle
GROUP BY paciente_id, nombre_completo;
