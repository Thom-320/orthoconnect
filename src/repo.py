"""Acceso a datos: SQL parametrizado para OrthoConnect."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Optional


def listar_pacientes(cur) -> list[tuple[Any, ...]]:
    cur.execute(
        """
        SELECT
            p.id,
            p.nombre,
            p.fecha_nacimiento,
            p.contacto,
            COALESCE(r.nombre, 'Directo') AS referido_por
        FROM pacientes p
        LEFT JOIN pacientes r ON p.referido_por = r.id
        ORDER BY p.id
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
        INSERT INTO pacientes (nombre, fecha_nacimiento, contacto, referido_por)
        VALUES (%s, %s::date, %s, %s)
        RETURNING id
        """,
        (nombre, fecha_nacimiento, contacto, referido_por_id),
    )
    return int(cur.fetchone()[0])


def listar_medicos_tratantes(cur) -> list[tuple[Any, ...]]:
    cur.execute(
        """
        SELECT id, nombre, rol AS especialidad, rol
        FROM personal
        WHERE rol IN ('Medico Senior', 'Medico Junior')
        ORDER BY id
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
        INSERT INTO tratamientos (paciente_id, medico_id, diagnostico, sesiones_estimadas, estado)
        VALUES (%s, %s, %s, %s, 'ACTIVO')
        RETURNING id
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
        INSERT INTO citas (
            tratamiento_id,
            fecha_hora,
            tipo_atencion,
            monto,
            pagado,
            asistida,
            personal_id
        )
        VALUES (%s, %s, %s, %s, FALSE, FALSE, %s)
        RETURNING id
        """,
        (tratamiento_id, fecha_hora, tipo_atencion, monto, profesional_empleado_id),
    )
    return int(cur.fetchone()[0])


def aplicar_pago(cur, tratamiento_id: int) -> Optional[tuple[Any, ...]]:
    cur.execute("SELECT * FROM aplicar_pago(%s)", (tratamiento_id,))
    return cur.fetchone()


def actualizar_evolucion(cur, cita_id: int, nota: str) -> int:
    cur.execute(
        """
        UPDATE citas
        SET nota_evolucion = %s,
            asistida = TRUE
        WHERE id = %s
        """,
        (nota, cita_id),
    )
    return cur.rowcount


def finalizar_tratamiento(cur, tratamiento_id: int) -> tuple[Any, ...]:
    cur.execute(
        """
        UPDATE tratamientos
        SET estado = 'FINALIZADO'
        WHERE id = %s
        RETURNING id, estado, eficacia_porcentaje, sesiones_estimadas
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
            c.id,
            c.fecha_hora,
            c.tipo_atencion,
            c.monto,
            t.id,
            t.diagnostico
        FROM citas c
        JOIN tratamientos t ON c.tratamiento_id = t.id
        WHERE t.paciente_id = %s
          AND c.pagado = FALSE
        ORDER BY c.fecha_hora
        """,
        (paciente_id,),
    )
    return cur.fetchall()


def historial_clinico(cur, paciente_id: int) -> list[tuple[Any, ...]]:
    cur.execute(
        """
        SELECT
            t.id,
            t.estado,
            t.diagnostico,
            p2.nombre AS medico,
            t.sesiones_estimadas,
            t.eficacia_porcentaje,
            c.id,
            c.fecha_hora,
            c.tipo_atencion,
            c.pagado,
            CASE WHEN c.asistida THEN 'ASISTIDA' ELSE 'PROGRAMADA' END AS estado_asistencia,
            c.nota_evolucion
        FROM tratamientos t
        JOIN personal p2 ON t.medico_id = p2.id
        LEFT JOIN citas c ON c.tratamiento_id = t.id
        WHERE t.paciente_id = %s
        ORDER BY t.id, c.fecha_hora NULLS LAST
        """,
        (paciente_id,),
    )
    return cur.fetchall()


def tratamientos_por_paciente(cur, paciente_id: int) -> list[tuple[Any, ...]]:
    cur.execute(
        """
        SELECT
            t.id,
            t.estado,
            t.diagnostico,
            p2.nombre,
            t.sesiones_estimadas,
            t.eficacia_porcentaje,
            COUNT(c.id) AS citas_totales,
            COUNT(c.id) FILTER (WHERE c.asistida IS TRUE) AS citas_asistidas
        FROM tratamientos t
        JOIN personal p2 ON t.medico_id = p2.id
        LEFT JOIN citas c ON c.tratamiento_id = t.id
        WHERE t.paciente_id = %s
        GROUP BY t.id, t.estado, t.diagnostico, p2.nombre, t.sesiones_estimadas, t.eficacia_porcentaje
        ORDER BY t.id
        """,
        (paciente_id,),
    )
    return cur.fetchall()


def listar_tratamientos(cur) -> list[tuple[Any, ...]]:
    cur.execute(
        """
        SELECT
            t.id,
            p.nombre,
            pr.nombre,
            t.diagnostico,
            t.sesiones_estimadas,
            t.estado,
            COALESCE(t.eficacia_porcentaje::text || '%', '—')
        FROM tratamientos t
        JOIN pacientes p ON p.id = t.paciente_id
        JOIN personal pr ON pr.id = t.medico_id
        ORDER BY t.id
        """
    )
    return cur.fetchall()


def organigrama_empleados(cur) -> list[tuple[Any, ...]]:
    cur.execute(
        """
        SELECT
            id,
            nombre,
            rol AS especialidad,
            supervisor,
            rol,
            nivel,
            ruta_orden
        FROM arbol_mando
        ORDER BY ruta_orden
        """
    )
    return cur.fetchall()


def reporte_adherencia(cur) -> list[tuple[Any, ...]]:
    cur.execute(
        """
        SELECT nombre, promedio_intervalo, estado_adherencia
        FROM reporte_adherencia
        ORDER BY nombre
        """
    )
    return cur.fetchall()


def cadena_referidos(cur) -> list[tuple[Any, ...]]:
    cur.execute(
        """
        SELECT id, nombre, nivel, cadena
        FROM linaje_confianza
        ORDER BY cadena
        """
    )
    return cur.fetchall()


def reporte_eficacia(cur) -> list[tuple[Any, ...]]:
    cur.execute(
        """
        SELECT
            t.id,
            p.nombre,
            pr.nombre,
            t.diagnostico,
            t.sesiones_estimadas,
            COUNT(c.id) FILTER (WHERE c.asistida IS TRUE) AS sesiones_asistidas,
            t.eficacia_porcentaje,
            t.estado
        FROM tratamientos t
        JOIN pacientes p ON p.id = t.paciente_id
        JOIN personal pr ON pr.id = t.medico_id
        LEFT JOIN citas c ON c.tratamiento_id = t.id
        GROUP BY t.id, p.nombre, pr.nombre, t.diagnostico, t.sesiones_estimadas, t.eficacia_porcentaje, t.estado
        ORDER BY t.id
        """
    )
    return cur.fetchall()


def tratamiento_existe(cur, tratamiento_id: int) -> bool:
    cur.execute("SELECT 1 FROM tratamientos WHERE id = %s", (tratamiento_id,))
    return cur.fetchone() is not None


def cita_existe(cur, cita_id: int) -> bool:
    cur.execute("SELECT 1 FROM citas WHERE id = %s", (cita_id,))
    return cur.fetchone() is not None
