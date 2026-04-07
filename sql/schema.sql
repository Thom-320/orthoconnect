-- OrthoConnect: esquema, triggers, vistas y función de pago
-- PostgreSQL

DROP TRIGGER IF EXISTS trg_auditoria_evolucion ON cita;
DROP TRIGGER IF EXISTS trg_morosidad_agenda ON cita;
DROP TRIGGER IF EXISTS trg_eficacia_tratamiento ON tratamiento;

DROP VIEW IF EXISTS v_reporte_adherencia;
DROP VIEW IF EXISTS v_cadena_referidos;
DROP VIEW IF EXISTS v_organigrama;

DROP FUNCTION IF EXISTS fn_aplicar_pago(INTEGER);
DROP FUNCTION IF EXISTS fn_check_morosidad();
DROP FUNCTION IF EXISTS fn_calcular_eficacia_tratamiento();
DROP FUNCTION IF EXISTS fn_auditoria_evolucion();

DROP TABLE IF EXISTS auditoria_evolucion;
DROP TABLE IF EXISTS cita;
DROP TABLE IF EXISTS tratamiento;
DROP TABLE IF EXISTS paciente;
DROP TABLE IF EXISTS empleado;

CREATE TABLE empleado (
    empleado_id         SERIAL PRIMARY KEY,
    nombre_completo     VARCHAR(200) NOT NULL,
    rol                 VARCHAR(30) NOT NULL
        CHECK (rol IN ('MEDICO_SENIOR', 'MEDICO_JUNIOR', 'TECNICO', 'FISIOTERAPEUTA')),
    especialidad        VARCHAR(150) NOT NULL,
    supervisor_id       INTEGER REFERENCES empleado (empleado_id) ON DELETE SET NULL
);

CREATE TABLE paciente (
    paciente_id             SERIAL PRIMARY KEY,
    nombre_completo         VARCHAR(200) NOT NULL,
    fecha_nacimiento        DATE NOT NULL,
    contacto                VARCHAR(80) NOT NULL,
    referido_por_paciente_id INTEGER REFERENCES paciente (paciente_id) ON DELETE SET NULL
);

CREATE TABLE tratamiento (
    tratamiento_id      SERIAL PRIMARY KEY,
    paciente_id         INTEGER NOT NULL REFERENCES paciente (paciente_id) ON DELETE CASCADE,
    medico_empleado_id  INTEGER NOT NULL REFERENCES empleado (empleado_id) ON DELETE RESTRICT,
    diagnostico         TEXT NOT NULL,
    sesiones_estimadas  INTEGER NOT NULL CHECK (sesiones_estimadas > 0),
    estado              VARCHAR(20) NOT NULL DEFAULT 'ACTIVO'
        CHECK (estado IN ('ACTIVO', 'FINALIZADO')),
    eficacia_porcentaje NUMERIC(10, 2)
);

CREATE TABLE cita (
    cita_id         SERIAL PRIMARY KEY,
    tratamiento_id  INTEGER NOT NULL REFERENCES tratamiento (tratamiento_id) ON DELETE CASCADE,
    fecha_hora      TIMESTAMP NOT NULL,
    tipo_atencion   VARCHAR(120) NOT NULL,
    monto           NUMERIC(12, 2) NOT NULL CHECK (monto >= 0),
    pagado          BOOLEAN NOT NULL DEFAULT FALSE,
    nota_evolucion  TEXT,
    profesional_empleado_id INTEGER REFERENCES empleado (empleado_id) ON DELETE SET NULL
);

CREATE TABLE auditoria_evolucion (
    auditoria_id    SERIAL PRIMARY KEY,
    cita_id         INTEGER NOT NULL REFERENCES cita (cita_id) ON DELETE CASCADE,
    nota_anterior   TEXT,
    nota_nueva      TEXT,
    usuario_editor  VARCHAR(200) NOT NULL,
    fecha_edicion   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_cita_tratamiento ON cita (tratamiento_id);
CREATE INDEX idx_cita_fecha ON cita (fecha_hora);
CREATE INDEX idx_tratamiento_paciente ON tratamiento (paciente_id);
CREATE INDEX idx_tratamiento_estado ON tratamiento (estado);

-- Morosidad: bloquear agendamiento si el paciente ya tiene 2+ citas pendientes (todas sus citas)
CREATE OR REPLACE FUNCTION fn_check_morosidad()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_paciente_id INTEGER;
    v_pendientes  INTEGER;
BEGIN
    SELECT t.paciente_id INTO v_paciente_id
    FROM tratamiento t
    WHERE t.tratamiento_id = NEW.tratamiento_id;

    SELECT COUNT(*) INTO v_pendientes
    FROM cita c
    INNER JOIN tratamiento t2 ON c.tratamiento_id = t2.tratamiento_id
    WHERE t2.paciente_id = v_paciente_id
      AND c.pagado = FALSE;

    IF v_pendientes >= 2 THEN
        RAISE EXCEPTION 'BLOQUEO: El paciente tiene % citas pendientes. Debe ponerse al día.', v_pendientes
            USING ERRCODE = 'P0001';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_morosidad_agenda
    BEFORE INSERT ON cita
    FOR EACH ROW
    EXECUTE PROCEDURE fn_check_morosidad();

-- Eficacia al pasar a FINALIZADO: (estimadas / reales) * 100
CREATE OR REPLACE FUNCTION fn_calcular_eficacia_tratamiento()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_reales INTEGER;
BEGIN
    IF NEW.estado = 'FINALIZADO' AND (OLD.estado IS DISTINCT FROM 'FINALIZADO') THEN
        SELECT COUNT(*) INTO v_reales FROM cita WHERE tratamiento_id = NEW.tratamiento_id;
        IF v_reales = 0 THEN
            NEW.eficacia_porcentaje := NULL;
        ELSE
            NEW.eficacia_porcentaje := ROUND(
                (NEW.sesiones_estimadas::NUMERIC / v_reales::NUMERIC) * 100,
                2
            );
        END IF;
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_eficacia_tratamiento
    BEFORE UPDATE ON tratamiento
    FOR EACH ROW
    EXECUTE PROCEDURE fn_calcular_eficacia_tratamiento();

-- Auditoría de notas de evolución
CREATE OR REPLACE FUNCTION fn_auditoria_evolucion()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_user TEXT;
BEGIN
    IF TG_OP = 'UPDATE'
       AND (OLD.nota_evolucion IS DISTINCT FROM NEW.nota_evolucion) THEN
        v_user := current_setting('application_name', true);
        IF v_user IS NULL OR v_user = '' THEN
            v_user := 'desconocido';
        END IF;
        INSERT INTO auditoria_evolucion (cita_id, nota_anterior, nota_nueva, usuario_editor)
        VALUES (OLD.cita_id, OLD.nota_evolucion, NEW.nota_evolucion, v_user);
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_auditoria_evolucion
    AFTER UPDATE ON cita
    FOR EACH ROW
    EXECUTE PROCEDURE fn_auditoria_evolucion();

-- Pago: salda la cita pendiente más antigua del tratamiento
CREATE OR REPLACE FUNCTION fn_aplicar_pago(p_tratamiento_id INTEGER)
RETURNS TABLE (
    cita_id_pagada INTEGER,
    fecha_hora_pago TIMESTAMP,
    tipo_atencion_pago VARCHAR,
    monto_pagado NUMERIC
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_cita INTEGER;
BEGIN
    SELECT c.cita_id INTO v_cita
    FROM cita c
    WHERE c.tratamiento_id = p_tratamiento_id
      AND c.pagado = FALSE
    ORDER BY c.fecha_hora ASC
    LIMIT 1
    FOR UPDATE OF c;

    IF v_cita IS NULL THEN
        RAISE EXCEPTION 'INFO:NO_HAY_DEUDAS: No hay citas pendientes de pago para este tratamiento.'
            USING ERRCODE = 'P0001';
    END IF;

    UPDATE cita SET pagado = TRUE WHERE cita.cita_id = v_cita;

    RETURN QUERY
    SELECT c.cita_id, c.fecha_hora, c.tipo_atencion::VARCHAR(120), c.monto
    FROM cita c
    WHERE c.cita_id = v_cita;
END;
$$;

-- Vista: organigrama (jerarquía completa desde seniors)
CREATE OR REPLACE VIEW v_organigrama AS
WITH RECURSIVE arbol AS (
    SELECT
        e.empleado_id,
        e.nombre_completo,
        e.rol,
        e.especialidad,
        e.supervisor_id,
        0 AS nivel,
        LPAD('', 0, ' ') || e.nombre_completo AS orden_texto
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
        a.orden_texto || '>' || e.nombre_completo
    FROM empleado e
    INNER JOIN arbol a ON e.supervisor_id = a.empleado_id
)
SELECT
    empleado_id,
    nombre_completo,
    rol,
    especialidad,
    supervisor_id,
    nivel
FROM arbol;

-- Cadena de referidos (árbol desde pacientes directos)
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
    INNER JOIN cadena c ON p.referido_por_paciente_id = c.paciente_id
)
SELECT paciente_id, nombre_completo, referido_por_paciente_id, nivel, cadena_texto
FROM cadena;

-- Adherencia: ventanas para días entre citas y clasificación
CREATE OR REPLACE VIEW v_reporte_adherencia AS
WITH citas_por_paciente AS (
    SELECT
        p.paciente_id,
        p.nombre_completo,
        c.fecha_hora,
        LAG(c.fecha_hora) OVER (
            PARTITION BY p.paciente_id
            ORDER BY c.fecha_hora
        ) AS fecha_previa
    FROM cita c
    INNER JOIN tratamiento t ON c.tratamiento_id = t.tratamiento_id
    INNER JOIN paciente p ON t.paciente_id = p.paciente_id
),
intervalos AS (
    SELECT
        paciente_id,
        nombre_completo,
        EXTRACT(EPOCH FROM (fecha_hora - fecha_previa)) / 86400.0 AS dias_entre
    FROM citas_por_paciente
    WHERE fecha_previa IS NOT NULL
),
agg AS (
    SELECT
        paciente_id,
        nombre_completo,
        ROUND(AVG(dias_entre)::NUMERIC, 1) AS promedio_dias_entre_citas
    FROM intervalos
    GROUP BY paciente_id, nombre_completo
)
SELECT
    paciente_id,
    nombre_completo,
    promedio_dias_entre_citas,
    CASE
        WHEN promedio_dias_entre_citas <= 7 THEN 'ALTA (Ideal)'
        WHEN promedio_dias_entre_citas <= 15 THEN 'MEDIA (Seguimiento)'
        ELSE 'BAJA (Riesgo de Abandono)'
    END AS estado_adherencia
FROM agg;
