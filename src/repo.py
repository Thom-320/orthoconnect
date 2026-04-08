"""Acceso a datos: SQL parametrizado para OrthoConnect."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

import psycopg2


def listar_pacientes(cur) -> list[tuple[Any, ...]]:
    cur.execute(
        """
        SELECT
            p.paciente_id,
            p.nombre_completo,
            p.fecha_nacimiento,
            p.contacto,
            COALESCE(r.nombre_completo, 'Directo') AS referido_por
        FROM paciente p
        LEFT JOIN paciente r ON p.referido_por_paciente_id = r.paciente_id
        ORDER BY p.paciente_id
        """
    )
    return cur.fetchall()


def insertar_paciente(
    cur,
    nombre: str,
    fecha_nacimiento: str,
    contacto: str,
    referido_por_id: Optional[int],
) -> int:
    cur.execute(
        """
        INSERT INTO paciente (nombre_completo, fecha_nacimiento, contacto, referido_por_paciente_id)
        VALUES (%s, %s::date, %s, %s)
        RETURNING paciente_id
        """,
        (nombre, fecha_nacimiento, contacto, referido_por_id),
    )
    row = cur.fetchone()
    return int(row[0])


def listar_medicos_tratantes(cur) -> list[tuple[Any, ...]]:
    cur.execute(
        """
        SELECT empleado_id, nombre_completo, especialidad, rol
        FROM empleado
        WHERE rol IN ('MEDICO_SENIOR', 'MEDICO_JUNIOR')
        ORDER BY empleado_id
        """
    )
    return cur.fetchall()


def insertar_tratamiento(
    cur,
    paciente_id: int,
    medico_empleado_id: int,
    diagnostico: str,
    sesiones_estimadas: int,
) -> int:
    cur.execute(
        """
        INSERT INTO tratamiento (paciente_id, medico_empleado_id, diagnostico, sesiones_estimadas, estado)
        VALUES (%s, %s, %s, %s, 'ACTIVO')
        RETURNING tratamiento_id
        """,
        (paciente_id, medico_empleado_id, diagnostico, sesiones_estimadas),
    )
    return int(cur.fetchone()[0])


def insertar_cita(
    cur,
    tratamiento_id: int,
    fecha_hora: datetime,
    tipo_atencion: str,
    monto: Decimal,
    profesional_empleado_id: Optional[int],
) -> int:
    cur.execute(
        """
        INSERT INTO cita (
            tratamiento_id,
            fecha_hora,
            tipo_atencion,
            monto,
            pagado,
            estado_asistencia,
            profesional_empleado_id
        )
        VALUES (%s, %s, %s, %s, FALSE, 'PROGRAMADA', %s)
        RETURNING cita_id
        """,
        (tratamiento_id, fecha_hora, tipo_atencion, monto, profesional_empleado_id),
    )
    return int(cur.fetchone()[0])


def aplicar_pago(cur, tratamiento_id: int) -> Optional[tuple[Any, ...]]:
    cur.execute("SELECT * FROM fn_aplicar_pago(%s)", (tratamiento_id,))
    return cur.fetchone()


def actualizar_evolucion(cur, cita_id: int, nota: str) -> int:
    cur.execute(
        """
        UPDATE cita
        SET nota_evolucion = %s,
            estado_asistencia = 'ASISTIDA'
        WHERE cita_id = %s
        """,
        (nota, cita_id),
    )
    return cur.rowcount


def finalizar_tratamiento(cur, tratamiento_id: int) -> tuple[Any, ...]:
    cur.execute(
        """
        UPDATE tratamiento SET estado = 'FINALIZADO' WHERE tratamiento_id = %s
        RETURNING tratamiento_id, estado, eficacia_porcentaje, sesiones_estimadas
        """,
        (tratamiento_id,),
    )
    row = cur.fetchone()
    if row is None:
        raise ValueError("Tratamiento no encontrado.")
    return row


def deudas_paciente(cur, paciente_id: int) -> list[tuple[Any, ...]]:
    cur.execute(
        """
        SELECT
            c.cita_id,
            c.fecha_hora,
            c.tipo_atencion,
            c.monto,
            t.tratamiento_id,
            t.diagnostico
        FROM cita c
        INNER JOIN tratamiento t ON c.tratamiento_id = t.tratamiento_id
        WHERE t.paciente_id = %s AND c.pagado = FALSE
        ORDER BY c.fecha_hora
        """,
        (paciente_id,),
    )
    return cur.fetchall()


def historial_clinico(cur, paciente_id: int) -> list[tuple[Any, ...]]:
    cur.execute(
        """
        SELECT
            t.tratamiento_id,
            t.estado,
            t.diagnostico,
            e.nombre_completo AS medico,
            t.sesiones_estimadas,
            t.eficacia_porcentaje,
            c.cita_id,
            c.fecha_hora,
            c.tipo_atencion,
            c.pagado,
            c.estado_asistencia,
            c.nota_evolucion
        FROM tratamiento t
        INNER JOIN empleado e ON t.medico_empleado_id = e.empleado_id
        LEFT JOIN cita c ON c.tratamiento_id = t.tratamiento_id
        WHERE t.paciente_id = %s
        ORDER BY t.tratamiento_id, c.fecha_hora NULLS LAST
        """,
        (paciente_id,),
    )
    return cur.fetchall()


def tratamientos_por_paciente(cur, paciente_id: int) -> list[tuple[Any, ...]]:
    cur.execute(
        """
        SELECT
            t.tratamiento_id,
            t.estado,
            t.diagnostico,
            e.nombre_completo,
            t.sesiones_estimadas,
            t.eficacia_porcentaje,
            (SELECT COUNT(*) FROM cita c WHERE c.tratamiento_id = t.tratamiento_id) AS citas_totales,
            (
                SELECT COUNT(*)
                FROM cita c
                WHERE c.tratamiento_id = t.tratamiento_id
                  AND c.estado_asistencia = 'ASISTIDA'
            ) AS citas_asistidas
        FROM tratamiento t
        INNER JOIN empleado e ON t.medico_empleado_id = e.empleado_id
        WHERE t.paciente_id = %s
        ORDER BY t.tratamiento_id
        """,
        (paciente_id,),
    )
    return cur.fetchall()


def listar_tratamientos(cur) -> list[tuple[Any, ...]]:
    cur.execute(
        """
        SELECT
            t.tratamiento_id,
            p.nombre_completo,
            e.nombre_completo,
            t.diagnostico,
            t.sesiones_estimadas,
            t.estado,
            COALESCE(t.eficacia_porcentaje::text || '%', '—')
        FROM tratamiento t
        JOIN paciente p ON p.paciente_id = t.paciente_id
        JOIN empleado e ON e.empleado_id = t.medico_empleado_id
        ORDER BY t.tratamiento_id
        """
    )
    return cur.fetchall()


def organigrama_empleados(cur) -> list[tuple[Any, ...]]:
    cur.execute(
        """
        SELECT
            empleado_id,
            nombre_completo,
            especialidad,
            supervisor_id,
            rol,
            nivel,
            ruta_orden
        FROM v_organigrama
        ORDER BY ruta_orden
        """
    )
    return cur.fetchall()


def reporte_adherencia(cur) -> list[tuple[Any, ...]]:
    cur.execute(
        """
        SELECT nombre_completo, promedio_dias_entre_citas, estado_adherencia
        FROM v_reporte_adherencia
        ORDER BY nombre_completo
        """
    )
    return cur.fetchall()


def cadena_referidos(cur) -> list[tuple[Any, ...]]:
    cur.execute(
        """
        SELECT paciente_id, nombre_completo, nivel, cadena_texto
        FROM v_cadena_referidos
        ORDER BY cadena_texto
        """
    )
    return cur.fetchall()


def reporte_eficacia(cur) -> list[tuple[Any, ...]]:
    cur.execute(
        """
        SELECT
            t.tratamiento_id,
            p.nombre_completo,
            e.nombre_completo,
            t.diagnostico,
            t.sesiones_estimadas,
            COUNT(c.cita_id) FILTER (WHERE c.estado_asistencia = 'ASISTIDA') AS sesiones_asistidas,
            t.eficacia_porcentaje,
            t.estado
        FROM tratamiento t
        JOIN paciente p ON p.paciente_id = t.paciente_id
        JOIN empleado e ON e.empleado_id = t.medico_empleado_id
        LEFT JOIN cita c ON c.tratamiento_id = t.tratamiento_id
        GROUP BY
            t.tratamiento_id,
            p.nombre_completo,
            e.nombre_completo,
            t.diagnostico,
            t.sesiones_estimadas,
            t.eficacia_porcentaje,
            t.estado
        ORDER BY t.tratamiento_id
        """
    )
    return cur.fetchall()


def tratamiento_existe(cur, tratamiento_id: int) -> bool:
    cur.execute("SELECT 1 FROM tratamiento WHERE tratamiento_id = %s", (tratamiento_id,))
    return cur.fetchone() is not None


def cita_existe(cur, cita_id: int) -> bool:
    cur.execute("SELECT 1 FROM cita WHERE cita_id = %s", (cita_id,))
    return cur.fetchone() is not None
