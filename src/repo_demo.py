"""Repositorio demo en memoria para ejecutar el CLI sin PostgreSQL."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, date
from decimal import Decimal
from statistics import mean
from typing import Any, Optional


@dataclass
class DemoCursor:
    data: "DemoData"

    def __enter__(self) -> "DemoCursor":
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        return False


class DemoConnection:
    def __init__(self) -> None:
        self.data = DemoData()

    def cursor(self) -> DemoCursor:
        return DemoCursor(self.data)

    def commit(self) -> None:
        return

    def rollback(self) -> None:
        return

    def close(self) -> None:
        return


class DemoData:
    def __init__(self) -> None:
        self.app_user = "demo"
        self.empleados: list[dict[str, Any]] = [
            {"empleado_id": 1, "nombre_completo": "Dr. Gregory House", "rol": "MEDICO_SENIOR", "especialidad": "Ortopedia Senior", "supervisor_id": None},
            {"empleado_id": 2, "nombre_completo": "Dr. Shaun Murphy", "rol": "MEDICO_JUNIOR", "especialidad": "Ortopedia Junior", "supervisor_id": 1},
            {"empleado_id": 3, "nombre_completo": "Lic. Wilson", "rol": "FISIOTERAPEUTA", "especialidad": "Fisioterapia", "supervisor_id": 2},
            {"empleado_id": 4, "nombre_completo": "Dra. Meredith Grey", "rol": "MEDICO_SENIOR", "especialidad": "Cirugia Ortopedica", "supervisor_id": None},
            {"empleado_id": 5, "nombre_completo": "Dra. Lexie Grey", "rol": "MEDICO_JUNIOR", "especialidad": "Ortopedia General", "supervisor_id": 4},
            {"empleado_id": 6, "nombre_completo": "Dr. Derek Shepherd", "rol": "MEDICO_SENIOR", "especialidad": "Neuro-Ortopedia", "supervisor_id": None},
            {"empleado_id": 7, "nombre_completo": "Ft. Jo Wilson", "rol": "FISIOTERAPEUTA", "especialidad": "Fisioterapia Deportiva", "supervisor_id": 6},
        ]
        self.pacientes: list[dict[str, Any]] = [
            {"paciente_id": 1, "nombre_completo": "Juan Perez", "fecha_nacimiento": date(1990, 5, 15), "contacto": "555-0101", "referido_por_paciente_id": None},
            {"paciente_id": 2, "nombre_completo": "Maria Lopez", "fecha_nacimiento": date(1985, 10, 20), "contacto": "555-0202", "referido_por_paciente_id": 1},
            {"paciente_id": 3, "nombre_completo": "Pedro Gomez", "fecha_nacimiento": date(1992, 1, 10), "contacto": "555-0303", "referido_por_paciente_id": 2},
            {"paciente_id": 4, "nombre_completo": "Carlos Ruiz", "fecha_nacimiento": date(1978, 3, 12), "contacto": "3001112233", "referido_por_paciente_id": None},
        ]
        self.tratamientos: list[dict[str, Any]] = [
            {"tratamiento_id": 1, "paciente_id": 1, "medico_empleado_id": 1, "diagnostico": "Fractura de femur", "sesiones_estimadas": 10, "estado": "ACTIVO", "eficacia_porcentaje": None},
            {"tratamiento_id": 2, "paciente_id": 2, "medico_empleado_id": 4, "diagnostico": "Reconstruccion de LCA", "sesiones_estimadas": 12, "estado": "FINALIZADO", "eficacia_porcentaje": Decimal("400.00")},
            {"tratamiento_id": 3, "paciente_id": 4, "medico_empleado_id": 6, "diagnostico": "Fractura", "sesiones_estimadas": 3, "estado": "ACTIVO", "eficacia_porcentaje": None},
        ]
        self.citas: list[dict[str, Any]] = [
            {"cita_id": 1, "tratamiento_id": 1, "fecha_hora": datetime(2026, 3, 1, 8, 0), "tipo_atencion": "Consulta inicial", "monto": Decimal("80000"), "pagado": False, "nota_evolucion": None, "profesional_empleado_id": 1},
            {"cita_id": 2, "tratamiento_id": 1, "fecha_hora": datetime(2026, 3, 5, 9, 0), "tipo_atencion": "Fisioterapia 1", "monto": Decimal("50000"), "pagado": True, "nota_evolucion": "Buena evolucion", "profesional_empleado_id": 3},
            {"cita_id": 3, "tratamiento_id": 1, "fecha_hora": datetime(2026, 3, 22, 0, 0), "tipo_atencion": "Sesion control", "monto": Decimal("50000"), "pagado": False, "nota_evolucion": None, "profesional_empleado_id": 3},
            {"cita_id": 4, "tratamiento_id": 2, "fecha_hora": datetime(2026, 1, 5, 8, 0), "tipo_atencion": "Fisioterapia", "monto": Decimal("60000"), "pagado": True, "nota_evolucion": "Paciente inicia fase de movilidad pasiva", "profesional_empleado_id": 7},
            {"cita_id": 5, "tratamiento_id": 2, "fecha_hora": datetime(2026, 1, 8, 8, 0), "tipo_atencion": "Fisioterapia", "monto": Decimal("60000"), "pagado": True, "nota_evolucion": "Se observa edema leve", "profesional_empleado_id": 7},
            {"cita_id": 6, "tratamiento_id": 2, "fecha_hora": datetime(2026, 1, 12, 8, 0), "tipo_atencion": "Fisioterapia", "monto": Decimal("60000"), "pagado": True, "nota_evolucion": None, "profesional_empleado_id": 7},
            {"cita_id": 7, "tratamiento_id": 3, "fecha_hora": datetime(2026, 1, 10, 10, 0), "tipo_atencion": "Consulta", "monto": Decimal("70000"), "pagado": True, "nota_evolucion": None, "profesional_empleado_id": 6},
            {"cita_id": 8, "tratamiento_id": 3, "fecha_hora": datetime(2026, 2, 15, 10, 0), "tipo_atencion": "Control", "monto": Decimal("50000"), "pagado": True, "nota_evolucion": None, "profesional_empleado_id": 6},
            {"cita_id": 9, "tratamiento_id": 3, "fecha_hora": datetime(2026, 3, 20, 10, 0), "tipo_atencion": "Fisioterapia", "monto": Decimal("50000"), "pagado": True, "nota_evolucion": None, "profesional_empleado_id": 7},
        ]
        self.auditoria_evolucion: list[dict[str, Any]] = []
        self.next_ids = {
            "paciente": 5,
            "tratamiento": 4,
            "cita": 10,
            "auditoria": 1,
        }


def _next_id(cur: DemoCursor, key: str) -> int:
    value = cur.data.next_ids[key]
    cur.data.next_ids[key] = value + 1
    return value


def _get_paciente(cur: DemoCursor, paciente_id: int) -> Optional[dict[str, Any]]:
    return next((p for p in cur.data.pacientes if p["paciente_id"] == paciente_id), None)


def _get_tratamiento(cur: DemoCursor, tratamiento_id: int) -> Optional[dict[str, Any]]:
    return next((t for t in cur.data.tratamientos if t["tratamiento_id"] == tratamiento_id), None)


def _get_empleado(cur: DemoCursor, empleado_id: int) -> Optional[dict[str, Any]]:
    return next((e for e in cur.data.empleados if e["empleado_id"] == empleado_id), None)


def listar_pacientes(cur: DemoCursor) -> list[tuple[Any, ...]]:
    rows: list[tuple[Any, ...]] = []
    for p in sorted(cur.data.pacientes, key=lambda x: x["paciente_id"]):
        ref = _get_paciente(cur, p["referido_por_paciente_id"]) if p["referido_por_paciente_id"] else None
        rows.append(
            (
                p["paciente_id"],
                p["nombre_completo"],
                p["fecha_nacimiento"],
                p["contacto"],
                ref["nombre_completo"] if ref else "Directo",
            )
        )
    return rows


def insertar_paciente(
    cur: DemoCursor,
    nombre: str,
    fecha_nacimiento: str,
    contacto: str,
    referido_por_id: Optional[int],
) -> int:
    if referido_por_id is not None and not _get_paciente(cur, referido_por_id):
        raise ValueError("Paciente referido no encontrado.")
    pid = _next_id(cur, "paciente")
    cur.data.pacientes.append(
        {
            "paciente_id": pid,
            "nombre_completo": nombre,
            "fecha_nacimiento": date.fromisoformat(fecha_nacimiento),
            "contacto": contacto,
            "referido_por_paciente_id": referido_por_id,
        }
    )
    return pid


def listar_medicos_tratantes(cur: DemoCursor) -> list[tuple[Any, ...]]:
    rows = [
        (e["empleado_id"], e["nombre_completo"], e["especialidad"], e["rol"])
        for e in cur.data.empleados
        if e["rol"] in ("MEDICO_SENIOR", "MEDICO_JUNIOR")
    ]
    rows.sort(key=lambda x: x[0])
    return rows


def insertar_tratamiento(
    cur: DemoCursor,
    paciente_id: int,
    medico_empleado_id: int,
    diagnostico: str,
    sesiones_estimadas: int,
) -> int:
    if not _get_paciente(cur, paciente_id):
        raise ValueError("Paciente no encontrado.")
    med = _get_empleado(cur, medico_empleado_id)
    if not med or med["rol"] not in ("MEDICO_SENIOR", "MEDICO_JUNIOR"):
        raise ValueError("Médico tratante inválido.")
    tid = _next_id(cur, "tratamiento")
    cur.data.tratamientos.append(
        {
            "tratamiento_id": tid,
            "paciente_id": paciente_id,
            "medico_empleado_id": medico_empleado_id,
            "diagnostico": diagnostico,
            "sesiones_estimadas": sesiones_estimadas,
            "estado": "ACTIVO",
            "eficacia_porcentaje": None,
        }
    )
    return tid


def tratamiento_existe(cur: DemoCursor, tratamiento_id: int) -> bool:
    return _get_tratamiento(cur, tratamiento_id) is not None


def insertar_cita(
    cur: DemoCursor,
    tratamiento_id: int,
    fecha_hora: datetime,
    tipo_atencion: str,
    monto: Decimal,
    profesional_empleado_id: Optional[int],
) -> int:
    t = _get_tratamiento(cur, tratamiento_id)
    if not t:
        raise ValueError("Tratamiento no encontrado.")

    paciente_id = t["paciente_id"]
    pendientes = 0
    for c in cur.data.citas:
        t2 = _get_tratamiento(cur, c["tratamiento_id"])
        if t2 and t2["paciente_id"] == paciente_id and not c["pagado"]:
            pendientes += 1
    if pendientes >= 2:
        raise ValueError(
            f"REGLA DE NEGOCIO VIOLADA: BLOQUEO: El paciente tiene {pendientes} citas pendientes. Debe ponerse al día."
        )

    if profesional_empleado_id is not None and not _get_empleado(cur, profesional_empleado_id):
        raise ValueError("Profesional no encontrado.")

    cid = _next_id(cur, "cita")
    cur.data.citas.append(
        {
            "cita_id": cid,
            "tratamiento_id": tratamiento_id,
            "fecha_hora": fecha_hora,
            "tipo_atencion": tipo_atencion,
            "monto": monto,
            "pagado": False,
            "nota_evolucion": None,
            "profesional_empleado_id": profesional_empleado_id,
        }
    )
    return cid


def aplicar_pago(cur: DemoCursor, tratamiento_id: int) -> Optional[tuple[Any, ...]]:
    pendientes = [c for c in cur.data.citas if c["tratamiento_id"] == tratamiento_id and not c["pagado"]]
    pendientes.sort(key=lambda x: x["fecha_hora"])
    if not pendientes:
        raise ValueError("No hay citas pendientes de pago para este tratamiento.")
    cita = pendientes[0]
    cita["pagado"] = True
    return (cita["cita_id"], cita["fecha_hora"], cita["tipo_atencion"], cita["monto"])


def cita_existe(cur: DemoCursor, cita_id: int) -> bool:
    return any(c["cita_id"] == cita_id for c in cur.data.citas)


def actualizar_evolucion(cur: DemoCursor, cita_id: int, nota: str) -> int:
    cita = next((c for c in cur.data.citas if c["cita_id"] == cita_id), None)
    if not cita:
        return 0
    old_note = cita["nota_evolucion"]
    cita["nota_evolucion"] = nota
    if old_note != nota:
        cur.data.auditoria_evolucion.append(
            {
                "auditoria_id": _next_id(cur, "auditoria"),
                "cita_id": cita_id,
                "nota_anterior": old_note,
                "nota_nueva": nota,
                "usuario_editor": cur.data.app_user,
                "fecha_edicion": datetime.now(),
            }
        )
    return 1


def finalizar_tratamiento(cur: DemoCursor, tratamiento_id: int) -> tuple[Any, ...]:
    t = _get_tratamiento(cur, tratamiento_id)
    if not t:
        raise ValueError("Tratamiento no encontrado.")
    if t["estado"] != "FINALIZADO":
        reales = sum(1 for c in cur.data.citas if c["tratamiento_id"] == tratamiento_id)
        if reales == 0:
            t["eficacia_porcentaje"] = None
        else:
            eficacia = (Decimal(t["sesiones_estimadas"]) / Decimal(reales)) * Decimal("100")
            t["eficacia_porcentaje"] = eficacia.quantize(Decimal("0.01"))
        t["estado"] = "FINALIZADO"
    return (t["tratamiento_id"], t["estado"], t["eficacia_porcentaje"], t["sesiones_estimadas"])


def deudas_paciente(cur: DemoCursor, paciente_id: int) -> list[tuple[Any, ...]]:
    rows: list[tuple[Any, ...]] = []
    for c in cur.data.citas:
        if c["pagado"]:
            continue
        t = _get_tratamiento(cur, c["tratamiento_id"])
        if not t or t["paciente_id"] != paciente_id:
            continue
        rows.append(
            (
                c["cita_id"],
                c["fecha_hora"],
                c["tipo_atencion"],
                c["monto"],
                t["tratamiento_id"],
                t["diagnostico"],
            )
        )
    rows.sort(key=lambda x: x[1])
    return rows


def historial_clinico(cur: DemoCursor, paciente_id: int) -> list[tuple[Any, ...]]:
    rows: list[tuple[Any, ...]] = []
    tratamientos = [t for t in cur.data.tratamientos if t["paciente_id"] == paciente_id]
    tratamientos.sort(key=lambda x: x["tratamiento_id"])
    for t in tratamientos:
        med = _get_empleado(cur, t["medico_empleado_id"])
        citas = [c for c in cur.data.citas if c["tratamiento_id"] == t["tratamiento_id"]]
        citas.sort(key=lambda x: x["fecha_hora"])
        if not citas:
            rows.append(
                (
                    t["tratamiento_id"],
                    t["estado"],
                    t["diagnostico"],
                    med["nombre_completo"] if med else "N/D",
                    t["sesiones_estimadas"],
                    t["eficacia_porcentaje"],
                    None,
                    None,
                    None,
                    None,
                    None,
                )
            )
            continue
        for c in citas:
            rows.append(
                (
                    t["tratamiento_id"],
                    t["estado"],
                    t["diagnostico"],
                    med["nombre_completo"] if med else "N/D",
                    t["sesiones_estimadas"],
                    t["eficacia_porcentaje"],
                    c["cita_id"],
                    c["fecha_hora"],
                    c["tipo_atencion"],
                    c["pagado"],
                    c["nota_evolucion"],
                )
            )
    return rows


def tratamientos_por_paciente(cur: DemoCursor, paciente_id: int) -> list[tuple[Any, ...]]:
    rows: list[tuple[Any, ...]] = []
    for t in sorted(cur.data.tratamientos, key=lambda x: x["tratamiento_id"]):
        if t["paciente_id"] != paciente_id:
            continue
        med = _get_empleado(cur, t["medico_empleado_id"])
        n_citas = sum(1 for c in cur.data.citas if c["tratamiento_id"] == t["tratamiento_id"])
        rows.append(
            (
                t["tratamiento_id"],
                t["estado"],
                t["diagnostico"],
                med["nombre_completo"] if med else "N/D",
                t["sesiones_estimadas"],
                t["eficacia_porcentaje"],
                n_citas,
            )
        )
    return rows


def organigrama_empleados(cur: DemoCursor) -> list[tuple[Any, ...]]:
    rows = [
        (e["empleado_id"], e["nombre_completo"], e["especialidad"], e["supervisor_id"], e["rol"])
        for e in cur.data.empleados
    ]
    rows.sort(key=lambda x: x[0])
    return rows


def reporte_adherencia(cur: DemoCursor) -> list[tuple[Any, ...]]:
    by_paciente: dict[int, list[datetime]] = {}
    for c in cur.data.citas:
        t = _get_tratamiento(cur, c["tratamiento_id"])
        if not t:
            continue
        by_paciente.setdefault(t["paciente_id"], []).append(c["fecha_hora"])

    rows: list[tuple[Any, ...]] = []
    for paciente_id, fechas in by_paciente.items():
        fechas.sort()
        if len(fechas) < 2:
            continue
        dias = []
        for i in range(1, len(fechas)):
            dias.append((fechas[i] - fechas[i - 1]).total_seconds() / 86400.0)
        promedio = round(mean(dias), 1)
        if promedio <= 7:
            estado = "ALTA (Ideal)"
        elif promedio <= 15:
            estado = "MEDIA (Seguimiento)"
        else:
            estado = "BAJA (Riesgo de Abandono)"
        paciente = _get_paciente(cur, paciente_id)
        if paciente:
            rows.append((paciente["nombre_completo"], promedio, estado))

    rows.sort(key=lambda x: x[0])
    return rows


def cadena_referidos(cur: DemoCursor) -> list[tuple[Any, ...]]:
    rows: list[tuple[Any, ...]] = []
    children: dict[Optional[int], list[dict[str, Any]]] = {}
    for p in cur.data.pacientes:
        children.setdefault(p["referido_por_paciente_id"], []).append(p)
    for key in children:
        children[key].sort(key=lambda x: x["paciente_id"])

    def walk(parent_id: Optional[int], nivel: int, path: list[str]) -> None:
        for p in children.get(parent_id, []):
            next_path = path + [p["nombre_completo"]]
            rows.append((p["paciente_id"], p["nombre_completo"], nivel, " -> ".join(next_path)))
            walk(p["paciente_id"], nivel + 1, next_path)

    walk(None, 0, [])
    return rows
