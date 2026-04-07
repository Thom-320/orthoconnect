#!/usr/bin/env python3
"""
OrthoConnect v1.0 — CLI de consola (rich + psycopg2)
Ejecutar desde la raíz del proyecto: PYTHONPATH=. python -m src.main
"""
from __future__ import annotations

import sys
from collections import defaultdict
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Callable, Optional

import psycopg2
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Column, Table
from rich.theme import Theme

from src.db import connect, set_application_name
from src.db_errors import format_db_error, is_business_rule_violation
from src import repo

# ── Tema ──────────────────────────────────────────────────────────────────────
_THEME = Theme({
    "amber":     "#E8A838",
    "amber.dim": "#9A6E1A",
    "ok":        "bold #52B788",
    "err":       "bold #E05858",
    "warn":      "#E8A838",
    "muted":     "#6B7280",
    "label":     "bold #C0C4D0",
    "mono":      "#94A3B8",
    "hi":        "bold white",
    "paid":      "bold #52B788",
    "unpaid":    "bold #E05858",
    "senior":    "bold white",
    "junior":    "#E8A838",
    "physio":    "bold #52B788",
    "tech":      "#6B7280",
})

con = Console(theme=_THEME, highlight=False)


# ── Helpers visuales ───────────────────────────────────────────────────────────
def banner() -> None:
    con.print()
    con.rule("[amber bold]  SISTEMA ORTHOCONNECT v1.0  [/amber bold]", style="amber.dim")
    con.print()
    con.print("  [muted]1.[/muted] Módulo Administrativo  [muted](Pacientes, Tratamientos, Citas y Pagos)[/muted]")
    con.print("  [muted]2.[/muted] Módulo Médico          [muted](Evolución de cita y Cierre de tratamiento)[/muted]")
    con.print("  [muted]3.[/muted] Módulo de Consultas    [muted](Pacientes e Historias)[/muted]")
    con.print("  [muted]4.[/muted] Módulo Gerencial       [muted](Analítica y Jerarquía)[/muted]")
    con.print("  [muted]5.[/muted] Salir")
    con.print()


def section_header(title: str, breadcrumb: str = "") -> None:
    con.print()
    if breadcrumb:
        con.print(f"  [muted]{breadcrumb}[/muted]")
    con.print(f"  [hi]{title}[/hi]")
    con.print("  " + "─" * 52, style="muted")
    con.print()


def panel_ok(title: str, body: str = "") -> None:
    lines = f"[ok]✓  {title}[/ok]"
    if body:
        lines += f"\n[muted]   {body}[/muted]"
    con.print(Panel(lines, border_style="ok", padding=(0, 2), expand=False))


def panel_err(title: str, body: str = "") -> None:
    lines = f"[err]{title}[/err]"
    if body:
        lines += f"\n[muted]{body}[/muted]"
    con.print(
        Panel(lines, title="[err]REGLA DE NEGOCIO VIOLADA[/err]",
              border_style="err", padding=(0, 2))
    )


def panel_info(msg: str) -> None:
    con.print(Panel(f"[warn]{msg}[/warn]", border_style="amber.dim", padding=(0, 2), expand=False))


def ask(label: str, required: bool = False) -> str:
    while True:
        val = con.input(f"  [muted]›[/muted] [label]{label}[/label]: ").strip()
        if required and not val:
            con.print("  [err]! Campo obligatorio.[/err]")
            continue
        return val


def ask_int(label: str, min_v: int = 1, max_v: Optional[int] = None) -> Optional[int]:
    raw = con.input(f"  [muted]›[/muted] [label]{label}[/label]: ").strip()
    if not raw:
        return None
    try:
        v = int(raw)
    except ValueError:
        con.print("  [err]! Número inválido.[/err]")
        return None
    if v < min_v or (max_v is not None and v > max_v):
        con.print(f"  [err]! Valor fuera de rango ({min_v}–{max_v if max_v else '∞'}).[/err]")
        return None
    return v


def ask_decimal(label: str) -> Optional[Decimal]:
    raw = con.input(f"  [muted]›[/muted] [label]{label}[/label]: ").strip()
    try:
        return Decimal(raw)
    except (InvalidOperation, ValueError):
        con.print("  [err]! Monto inválido.[/err]")
        return None


def ask_datetime(label: str) -> Optional[datetime]:
    raw = con.input(
        f"  [muted]›[/muted] [label]{label}[/label] [muted](YYYY-MM-DD HH:MM)[/muted]: "
    ).strip()
    try:
        return datetime.strptime(raw, "%Y-%m-%d %H:%M")
    except ValueError:
        con.print("  [err]! Use el formato YYYY-MM-DD HH:MM.[/err]")
        return None


# ── DB action con spinner ──────────────────────────────────────────────────────
def run_db(conn, action: Callable, spinner_msg: str = "Procesando…") -> bool:
    try:
        with con.status(f"  [muted]{spinner_msg}[/muted]", spinner="dots", spinner_style="amber"):
            with conn.cursor() as cur:
                action(cur)
        conn.commit()
        return True
    except psycopg2.Error as e:
        conn.rollback()
        msg = format_db_error(e)
        if is_business_rule_violation(e):
            panel_err(msg)
        else:
            con.print(Panel(
                f"[err]{msg}[/err]", title="[err]Error de base de datos[/err]", border_style="err"
            ))
        return False
    except ValueError as ve:
        conn.rollback()
        con.print(f"  [err]✗ {ve}[/err]")
        return False


# ── Tablas ricas ───────────────────────────────────────────────────────────────
def tbl_pacientes(rows: list[tuple]) -> None:
    t = Table(
        Column("ID",     style="mono", justify="right", width=5),
        Column("Nombre", style="hi",   min_width=22),
        Column("Nacimiento", style="muted", width=12),
        Column("Contacto",   style="muted", width=15),
        Column("Referido por", style="amber"),
        box=box.SIMPLE_HEAD, header_style="label",
        show_edge=False, padding=(0, 1),
    )
    for pid, nom, fnac, cont, ref in rows:
        t.add_row(str(pid), str(nom), str(fnac), str(cont)[:15], str(ref))
    con.print("  ", end="")
    con.print(t)


# ── Módulo Administrativo ──────────────────────────────────────────────────────
def modulo_administrativo(conn) -> None:
    while True:
        con.print()
        con.rule("[amber]  MÓDULO ADMINISTRATIVO  [/amber]", style="amber.dim")
        con.print("  [muted]1.[/muted] Registrar Nuevo Paciente")
        con.print("  [muted]2.[/muted] Abrir Nuevo Tratamiento")
        con.print("  [muted]3.[/muted] Agendar Cita  [muted](Control Morosidad)[/muted]")
        con.print("  [muted]4.[/muted] Registrar Pago  [muted](Saldar Deuda)[/muted]")
        con.print("  [muted]5.[/muted] Volver")
        con.print()
        op = ask_int("Seleccione acción", min_v=1, max_v=5)
        if op is None:
            continue
        if op == 5:
            return
        if op == 1:
            _admin_nuevo_paciente(conn)
        elif op == 2:
            _admin_nuevo_tratamiento(conn)
        elif op == 3:
            _admin_agendar_cita(conn)
        elif op == 4:
            _admin_registrar_pago(conn)


def _admin_nuevo_paciente(conn) -> None:
    section_header("REGISTRO DE NUEVO PACIENTE", "Administrativo")
    nombre = ask("Nombre completo", required=True)
    if not nombre:
        return
    fn = ask("Fecha de nacimiento (YYYY-MM-DD)", required=True)
    cont = ask("Teléfono / Celular de contacto", required=True)
    if not fn or not cont:
        return

    ref = None
    sn = con.input(
        "  [muted]›[/muted] [label]¿Fue referido por otro paciente?[/label] [muted](s/n)[/muted]: "
    ).strip().lower()
    if sn == "s":
        with conn.cursor() as cur:
            rows = repo.listar_pacientes(cur)
        con.print()
        tbl_pacientes(rows)
        ref = ask_int("ID del paciente que lo refirió", min_v=1)
        if ref is None:
            return

    def ins(cur):
        nid = repo.insertar_paciente(cur, nombre, fn, cont, ref)
        panel_ok(f"PACIENTE REGISTRADO  ·  ID: {nid}  ·  {nombre}")

    run_db(conn, ins, "Registrando paciente…")


def _admin_nuevo_tratamiento(conn) -> None:
    section_header("ABRIR TRATAMIENTO", "Administrativo")
    with conn.cursor() as cur:
        pacs = repo.listar_pacientes(cur)
        meds = repo.listar_medicos_tratantes(cur)
    tbl_pacientes(pacs)

    pid = ask_int("ID del Paciente", min_v=1)
    if pid is None:
        return

    t = Table(
        Column("ID",  style="mono", width=4),
        Column("Médico", style="hi"),
        Column("Rol",    style="muted"),
        Column("Especialidad", style="amber"),
        box=box.SIMPLE_HEAD, header_style="label", show_edge=False, padding=(0, 1),
    )
    for m in meds:
        t.add_row(str(m[0]), str(m[1]), str(m[3]), str(m[2]))
    con.print("  ", end="")
    con.print(t)

    mid = ask_int("ID del médico tratante", min_v=1)
    if mid is None:
        return
    diag = ask("Diagnóstico", required=True)
    ses = ask_int("Sesiones estimadas", min_v=1)
    if ses is None:
        return

    def ins_t(cur):
        tid = repo.insertar_tratamiento(cur, pid, mid, diag, ses)
        panel_ok(f"Tratamiento creado  ·  ID: {tid}")

    run_db(conn, ins_t, "Creando tratamiento…")


def _admin_agendar_cita(conn) -> None:
    section_header("AGENDAR CITA", "Administrativo · Control de Morosidad")
    tid = ask_int("ID del Tratamiento", min_v=1)
    if tid is None:
        return
    fh = ask_datetime("Fecha y Hora")
    if fh is None:
        return
    monto = ask_decimal("Monto a cobrar")
    if monto is None:
        return
    tipo = ask("Tipo de atención", required=True)
    prof_raw = con.input(
        "  [muted]›[/muted] [label]ID profesional[/label] [muted](Enter = omitir)[/muted]: "
    ).strip()
    prof: Optional[int] = None
    if prof_raw:
        try:
            prof = int(prof_raw)
        except ValueError:
            con.print("  [err]! ID de profesional inválido.[/err]")
            return

    def ins_c(cur):
        if not repo.tratamiento_existe(cur, tid):
            raise ValueError("Tratamiento no encontrado.")
        cid = repo.insertar_cita(cur, tid, fh, tipo, monto, prof)
        panel_ok(f"Cita agendada con éxito  ·  ID cita: {cid}")

    run_db(conn, ins_c, "Agendando cita…")


def _admin_registrar_pago(conn) -> None:
    section_header("REGISTRAR PAGO  —  Saldar Deuda Antigua", "Administrativo · FIFO")
    tid = ask_int("ID del Tratamiento", min_v=1)
    if tid is None:
        return

    def pay(cur):
        row = repo.aplicar_pago(cur, tid)
        if not row:
            raise ValueError("No se obtuvo resultado del pago.")
        cita_id, fecha, concepto, monto_v = row
        con.print(
            Panel(
                f"[ok]✓  ¡PAGO PROCESADO EXITOSAMENTE![/ok]\n\n"
                f"  [label]ID Cita:[/label]   [hi]{cita_id}[/hi]\n"
                f"  [label]Fecha:[/label]     [hi]{fecha}[/hi]\n"
                f"  [label]Concepto:[/label]  [hi]{concepto}[/hi]\n"
                f"  [label]Monto:[/label]     [hi]${monto_v}[/hi]",
                border_style="ok",
                padding=(0, 2),
            )
        )

    run_db(conn, pay, "Procesando pago…")


# ── Módulo Médico ──────────────────────────────────────────────────────────────
def modulo_medico(conn) -> None:
    while True:
        con.print()
        con.rule("[amber]  MÓDULO MÉDICO  [/amber]", style="amber.dim")
        con.print("  [muted]1.[/muted] Registrar Evolución de Cita")
        con.print("  [muted]2.[/muted] Finalizar Tratamiento  [muted](activa trigger de eficacia)[/muted]")
        con.print("  [muted]3.[/muted] Volver")
        con.print()
        op = ask_int("Acción", min_v=1, max_v=3)
        if op is None:
            continue
        if op == 3:
            return
        if op == 1:
            _medico_evolucion(conn)
        elif op == 2:
            _medico_finalizar(conn)


def _medico_evolucion(conn) -> None:
    section_header("REGISTRAR EVOLUCIÓN", "Médico")
    cid = ask_int("ID de la cita", min_v=1)
    if cid is None:
        return
    nota = ask("Nota de evolución", required=True)

    def upd(cur):
        if not repo.cita_existe(cur, cid):
            raise ValueError("Cita no encontrada.")
        n = repo.actualizar_evolucion(cur, cid, nota)
        if n == 0:
            raise ValueError("No se pudo actualizar la cita.")
        panel_ok("Evolución registrada", "Auditoría guardada en base de datos.")

    run_db(conn, upd, "Guardando nota…")


def _medico_finalizar(conn) -> None:
    section_header("FINALIZAR TRATAMIENTO", "Médico · Trigger de Eficacia")
    tid = ask_int("ID del Tratamiento a finalizar", min_v=1)
    if tid is None:
        return

    def fin(cur):
        if not repo.tratamiento_existe(cur, tid):
            raise ValueError("Tratamiento no encontrado.")
        row = repo.finalizar_tratamiento(cur, tid)
        _, _estado, eficacia, _sest = row
        efic_str = f"{eficacia}%" if eficacia is not None else "N/D"
        panel_ok(f"Tratamiento #{tid} cerrado", f"Eficacia calculada: {efic_str}")

    run_db(conn, fin, "Finalizando tratamiento…")


# ── Módulo Consultas ───────────────────────────────────────────────────────────
def modulo_consultas(conn) -> None:
    while True:
        con.print()
        con.rule("[amber]  MÓDULO DE CONSULTAS  [/amber]", style="amber.dim")
        con.print("  [muted]1.[/muted] Lista de Pacientes")
        con.print("  [muted]2.[/muted] Deudas de Paciente")
        con.print("  [muted]3.[/muted] Historial Clínico")
        con.print("  [muted]4.[/muted] Tratamientos por Paciente")
        con.print("  [muted]5.[/muted] Volver")
        con.print()
        op = ask_int("Acción", min_v=1, max_v=5)
        if op is None:
            continue
        if op == 5:
            return
        try:
            with conn.cursor() as cur:
                if op == 1:
                    rows = repo.listar_pacientes(cur)
                    con.print()
                    tbl_pacientes(rows)

                elif op == 2:
                    pid = ask_int("ID del paciente", min_v=1)
                    if pid is None:
                        continue
                    deudas = repo.deudas_paciente(cur, pid)
                    if not deudas:
                        panel_info("El paciente no tiene citas pendientes de pago.")
                    else:
                        t = Table(
                            Column("Cita",  style="mono", width=5),
                            Column("Trat.", style="mono", width=5),
                            Column("Fecha", style="muted"),
                            Column("Tipo",  style="hi"),
                            Column("Monto", justify="right", style="warn"),
                            Column("Diagnóstico", style="muted"),
                            box=box.SIMPLE_HEAD, header_style="label",
                            show_edge=False, padding=(0, 1),
                        )
                        for d in deudas:
                            cid, fh, tipo, mont, ttid, diag = d
                            t.add_row(str(cid), str(ttid), str(fh), str(tipo), f"${mont}", str(diag))
                        con.print("  ", end="")
                        con.print(t)

                elif op == 3:
                    pid = ask_int("ID del paciente", min_v=1)
                    if pid is None:
                        continue
                    rows = repo.historial_clinico(cur, pid)
                    _mostrar_historial(rows)

                elif op == 4:
                    pid = ask_int("ID del paciente", min_v=1)
                    if pid is None:
                        continue
                    rows = repo.tratamientos_por_paciente(cur, pid)
                    for r in rows:
                        t_id, est, diag, med, sest, efic, nc = r
                        badge = "[ok]FINALIZADO[/ok]" if est == "FINALIZADO" else "[warn]ACTIVO[/warn]"
                        con.print(f"\n  [hi]Tratamiento #{t_id}[/hi]  {badge}")
                        con.print(f"  [muted]Diagnóstico:[/muted] [label]{diag}[/label]")
                        con.print(f"  [muted]Médico:[/muted] {med}  "
                                  f"[muted]Estimadas:[/muted] {sest}  "
                                  f"[muted]Citas:[/muted] {nc}")
                        if efic is not None:
                            con.print(f"  [warn]Eficacia: {efic}%[/warn]")
        except psycopg2.Error as e:
            con.print(Panel(f"[err]{format_db_error(e)}[/err]", border_style="err"))


def _mostrar_historial(rows: list[tuple]) -> None:
    if not rows:
        panel_info("Sin datos para este paciente.")
        return
    current_tid = None
    for r in rows:
        tid, estado, diag, medico, ses_est, eficacia, cita_id, fecha, tipo, pagado, nota = r
        if tid != current_tid:
            current_tid = tid
            badge = "[ok]FINALIZADO[/ok]" if estado == "FINALIZADO" else "[warn]ACTIVO[/warn]"
            con.print(f"\n  [hi]TRATAMIENTO #{tid}[/hi]  {badge}")
            con.print(f"  [muted]Diagnóstico:[/muted] [label]{diag}[/label]")
            con.print(f"  [muted]Médico:[/muted] {medico}  [muted]Ses. Est.:[/muted] {ses_est}")
            if eficacia is not None:
                con.print(f"  [warn]Eficacia: {eficacia}%[/warn]")
            con.print("  " + "·" * 52, style="muted")
        if cita_id is None:
            continue
        marca = "[paid][X][/paid]" if pagado else "[unpaid][P][/unpaid]"
        nota_s = str(nota) if nota else "[muted]—[/muted]"
        con.print(f"  {marca}  [muted]{fecha}[/muted]  [label]{tipo}[/label]  {nota_s}")


# ── Módulo Gerencia ────────────────────────────────────────────────────────────
def modulo_gerencia(conn) -> None:
    while True:
        con.print()
        con.rule("[amber]  MÓDULO GERENCIAL  [/amber]", style="amber.dim")
        con.print("  [muted]1.[/muted] Organigrama  [muted](CTE Recursiva)[/muted]")
        con.print("  [muted]2.[/muted] Reporte de Adherencia  [muted](Window Functions)[/muted]")
        con.print("  [muted]3.[/muted] Cadena de Referidos  [muted](CTE Recursiva)[/muted]")
        con.print("  [muted]4.[/muted] Volver")
        con.print()
        op = ask_int("Acción", min_v=1, max_v=4)
        if op is None:
            continue
        if op == 4:
            return
        try:
            with conn.cursor() as cur:
                if op == 1:
                    rows = repo.organigrama_empleados(cur)
                    _mostrar_organigrama(rows)
                elif op == 2:
                    rows = repo.reporte_adherencia(cur)
                    _mostrar_adherencia(rows)
                elif op == 3:
                    rows = repo.cadena_referidos(cur)
                    _mostrar_referidos(rows)
        except psycopg2.Error as e:
            con.print(Panel(f"[err]{format_db_error(e)}[/err]", border_style="err"))


def _mostrar_organigrama(rows: list[tuple]) -> None:
    section_header("ORGANIGRAMA", "Gerencia · CTE Recursiva")
    by_sup: dict[Optional[int], list[tuple]] = defaultdict(list)
    for eid, nom, esp, sup, rol in rows:
        by_sup[sup].append((eid, nom, esp, rol))
    for k in by_sup:
        by_sup[k].sort(key=lambda x: x[1])

    _ROLE_COLOR = {
        "MEDICO_SENIOR": "senior",
        "MEDICO_JUNIOR": "junior",
        "FISIOTERAPEUTA": "physio",
        "TECNICO": "tech",
    }

    def walk(parent_id: Optional[int], nivel: int) -> None:
        for eid, nom, esp, rol in by_sup.get(parent_id, []):
            indent = "  " * nivel
            rc = _ROLE_COLOR.get(rol, "muted")
            con.print(f"  {indent}[{rc}]└─ {nom}[/{rc}]  [muted]{esp}[/muted]")
            walk(eid, nivel + 1)

    walk(None, 0)


def _mostrar_adherencia(rows: list[tuple]) -> None:
    section_header("REPORTE DE ADHERENCIA", "Gerencia · Window Functions")
    if not rows:
        panel_info("Sin datos de adherencia.")
        return
    t = Table(
        Column("Paciente", style="hi", min_width=22),
        Column("Prom. días", justify="right", style="mono", width=11),
        Column("Estado", min_width=30),
        box=box.SIMPLE_HEAD, header_style="label",
        show_edge=False, padding=(0, 1),
    )
    for nombre, prom, estado in rows:
        est_s = str(estado)
        if "ALTA" in est_s:
            cell = f"[ok]{est_s}[/ok]"
        elif "MEDIA" in est_s:
            cell = f"[warn]{est_s}[/warn]"
        else:
            cell = f"[err]{est_s}[/err]"
        t.add_row(str(nombre), str(prom), cell)
    con.print("  ", end="")
    con.print(t)


def _mostrar_referidos(rows: list[tuple]) -> None:
    section_header("CADENA DE REFERIDOS", "Gerencia · CTE Recursiva")
    for _pid, nombre, nivel, cadena in rows:
        indent = "  " * nivel
        if nivel == 0:
            con.print(f"\n  {indent}[hi]{nombre}[/hi]  [muted](Directo)[/muted]")
        else:
            parts = cadena.split(" -> ")
            path = " [muted]→[/muted] ".join(parts[:-1])
            con.print(f"  {indent}[amber]└─[/amber] [hi]{nombre}[/hi]  [muted]via {path}[/muted]")


# ── Menú principal ─────────────────────────────────────────────────────────────
def main_menu(conn) -> None:
    while True:
        banner()
        op = ask_int("Seleccione una opción", min_v=1, max_v=5)
        if op is None:
            continue
        if op == 5:
            con.print("\n  [muted]Hasta luego.[/muted]\n")
            return
        if op == 1:
            modulo_administrativo(conn)
        elif op == 2:
            modulo_medico(conn)
        elif op == 3:
            modulo_consultas(conn)
        elif op == 4:
            modulo_gerencia(conn)


# ── Entry point ────────────────────────────────────────────────────────────────
def main() -> int:
    con.print()
    con.rule("[amber bold]  ORTHOCONNECT v1.0  [/amber bold]", style="amber.dim")
    con.print()
    con.print("  [muted]Conexión:[/muted] PostgreSQL  [muted](psycopg2)[/muted]")
    con.print("  [muted]Aplique antes los scripts SQL del equipo de base de datos[/muted]")
    con.print("  [muted](véase sql/README.md).[/muted]")
    con.print()

    app_user = (
        con.input("  [muted]›[/muted] [label]Operador[/label] [muted](nombre para auditoría)[/muted]: ")
        .strip()
        or "cli"
    )

    con.print()
    con.print("  [muted]Conectando a PostgreSQL…[/muted]")
    try:
        conn_obj = connect()
    except psycopg2.Error as e:
        con.print(Panel(f"[err]No se pudo conectar: {e}[/err]", border_style="err"))
        return 1
    try:
        set_application_name(conn_obj, app_user)
        conn_obj.commit()
        main_menu(conn_obj)
    finally:
        conn_obj.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
