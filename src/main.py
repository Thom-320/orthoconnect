#!/usr/bin/env python3
"""
OrthoConnect v1.0 — CLI de consola (psycopg2).
Ejecutar desde la raíz del proyecto: python -m src.main
"""

from __future__ import annotations

import sys
from collections import defaultdict
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Callable, Optional

import psycopg2

from src.db import connect, set_application_name
from src.db_errors import format_db_error, is_business_rule_violation
from src import repo


def banner(title: str) -> None:
    w = max(40, len(title) + 8)
    line = "=" * w
    print(line)
    print(title.center(w))
    print(line)


def prompt_line(label: str) -> str:
    return input(label).strip()


def prompt_int(label: str, min_v: int = 1, max_v: Optional[int] = None) -> Optional[int]:
    raw = input(label).strip()
    if raw == "":
        return None
    try:
        v = int(raw)
    except ValueError:
        print("Ingrese un número entero válido.")
        return None
    if v < min_v or (max_v is not None and v > max_v):
        print(f"El valor debe estar entre {min_v} y {max_v if max_v is not None else '∞'}.")
        return None
    return v


def prompt_decimal(label: str) -> Optional[Decimal]:
    raw = input(label).strip()
    try:
        return Decimal(raw)
    except (InvalidOperation, ValueError):
        print("Monto inválido.")
        return None


def prompt_datetime(label: str) -> Optional[datetime]:
    raw = input(label).strip()
    try:
        return datetime.strptime(raw, "%Y-%m-%d %H:%M")
    except ValueError:
        print("Use el formato YYYY-MM-DD HH:MM")
        return None


def print_pacientes_table(rows: list[tuple]) -> None:
    print(f"{'ID':<5} {'NOMBRE':<25} {'F. NACIMIENTO':<15} {'CONTACTO':<15} {'REFERIDO POR':<20}")
    print("-" * 85)
    for r in rows:
        pid, nom, fnac, cont, ref = r
        print(f"{pid:<5} {str(nom)[:25]:<25} {str(fnac):<15} {str(cont)[:15]:<15} {str(ref)[:20]:<20}")


def run_db_action(conn, action: Callable) -> bool:
    """Ejecuta action(cur). Hace commit si OK; rollback y mensaje si error. Retorna éxito."""
    try:
        with conn.cursor() as cur:
            action(cur)
        conn.commit()
        return True
    except psycopg2.Error as e:
        conn.rollback()
        msg = format_db_error(e)
        if is_business_rule_violation(e):
            print(msg)
        else:
            print("Error de base de datos:\n" + msg)
        return False
    except ValueError as e:
        conn.rollback()
        print(str(e))
        return False


def modulo_administrativo(conn) -> None:
    while True:
        print("\n--- MÓDULO ADMINISTRATIVO ---")
        print("[1] Registrar Nuevo Paciente")
        print("[2] Abrir Nuevo Tratamiento")
        print("[3] Agendar Cita (Control Morosidad)")
        print("[4] Registrar Pago (Saldar Deuda)")
        print("[5] Volver")
        op = prompt_int("Seleccione acción: ", min_v=1, max_v=5)
        if op is None:
            continue
        if op == 5:
            return

        if op == 1:
            banner("REGISTRO DE NUEVO PACIENTE")
            nombre = prompt_line("Nombre completo: ")
            if not nombre:
                print("El nombre es obligatorio.")
                continue
            fn = prompt_line("Fecha de nacimiento (YYYY-MM-DD): ")
            cont = prompt_line("Teléfono/Celular de contacto: ")
            if not fn or not cont:
                print("Fecha y contacto son obligatorios.")
                continue
            ref = None
            sn = prompt_line("¿Fue referido por otro paciente? (S/N): ").lower()
            if sn == "s":
                with conn.cursor() as cur:
                    rows = repo.listar_pacientes(cur)
                print_pacientes_table(rows)
                ref = prompt_int("Ingrese el ID del paciente que lo refirió: ", min_v=1)
                if ref is None:
                    continue

            def ins(cur):
                new_id = repo.insertar_paciente(cur, nombre, fn, cont, ref)
                print(f"\n✅ PACIENTE REGISTRADO EXITOSAMENTE.")
                print(f"ID Asignado: {new_id} | Nombre: {nombre}")

            run_db_action(conn, ins)

        elif op == 2:
            with conn.cursor() as cur:
                pacs = repo.listar_pacientes(cur)
                meds = repo.listar_medicos_tratantes(cur)
            print_pacientes_table(pacs)
            pid = prompt_int("ID del Paciente: ", min_v=1)
            if pid is None:
                continue
            print("\nMédicos tratantes:")
            for m in meds:
                print(f"  [{m[0]}] {m[1]} — {m[3]} / {m[2]}")
            mid = prompt_int("ID del médico tratante: ", min_v=1)
            if mid is None:
                continue
            diag = prompt_line("Diagnóstico: ")
            if not diag:
                print("Diagnóstico obligatorio.")
                continue
            ses = prompt_int("Sesiones estimadas: ", min_v=1)
            if ses is None:
                continue

            def ins_t(cur):
                tid = repo.insertar_tratamiento(cur, pid, mid, diag, ses)
                print(f"Tratamiento creado. ID: {tid}")

            run_db_action(conn, ins_t)

        elif op == 3:
            tid = prompt_int("ID del Tratamiento: ", min_v=1)
            if tid is None:
                continue
            fh = prompt_datetime("Fecha y Hora (YYYY-MM-DD HH:MM): ")
            if fh is None:
                continue
            monto = prompt_decimal("Monto a cobrar: ")
            if monto is None:
                continue
            tipo = prompt_line("Tipo de atención: ")
            if not tipo:
                print("Tipo de atención obligatorio.")
                continue
            prof_raw = prompt_line("ID profesional que atiende (opcional, Enter omitir): ")
            prof: Optional[int] = None
            if prof_raw:
                try:
                    prof = int(prof_raw)
                except ValueError:
                    print("ID de profesional inválido.")
                    continue

            def ins_c(cur):
                if not repo.tratamiento_existe(cur, tid):
                    raise ValueError("Tratamiento no encontrado.")
                cid = repo.insertar_cita(cur, tid, fh, tipo, monto, prof)
                print(f"Cita agendada con éxito. ID cita: {cid}")

            run_db_action(conn, ins_c)

        elif op == 4:
            banner("REGISTRO DE PAGO (Saldar Deuda Antigua)")
            tid = prompt_int("Ingrese el ID del Tratamiento: ", min_v=1)
            if tid is None:
                continue

            def pay(cur):
                row = repo.aplicar_pago(cur, tid)
                if not row:
                    raise ValueError("No se obtuvo resultado del pago.")
                cita_id, fecha, concepto, monto = row
                print("\n✓" * 20)
                print("  ¡PAGO PROCESADO EXITOSAMENTE!")
                print("✓" * 20)
                print(f"  ID Cita:    {cita_id}")
                print(f"  Fecha:      {fecha}")
                print(f"  Concepto:   {concepto}")
                print(f"  Monto:      ${monto}")
                print("-" * 40)

            run_db_action(conn, pay)


def modulo_medico(conn) -> None:
    while True:
        print("\n[1] Registrar Evolución | [2] Finalizar Tratamiento")
        op = prompt_int("Acción: ", min_v=1, max_v=2)
        if op is None:
            continue
        if op == 1:
            cid = prompt_int("ID de la cita: ", min_v=1)
            if cid is None:
                continue
            nota = prompt_line("Nota de evolución: ")

            def upd(cur):
                if not repo.cita_existe(cur, cid):
                    raise ValueError("Cita no encontrada.")
                n = repo.actualizar_evolucion(cur, cid, nota)
                if n == 0:
                    raise ValueError("No se pudo actualizar la cita.")
                print("Evolución registrada (auditoría en base de datos si aplica).")

            if run_db_action(conn, upd):
                return
            continue

        tid = prompt_int("Ingrese ID del Tratamiento a finalizar: ", min_v=1)
        if tid is None:
            continue

        def fin(cur):
            if not repo.tratamiento_existe(cur, tid):
                raise ValueError("Tratamiento no encontrado.")
            row = repo.finalizar_tratamiento(cur, tid)
            _, _estado, eficacia, _sest = row
            eficacia_str = f"{eficacia}%" if eficacia is not None else "N/D"
            print(f"Tratamiento Cerrado. Eficacia calculada: {eficacia_str}")

        if run_db_action(conn, fin):
            return


def mostrar_historial(rows: list[tuple]) -> None:
    if not rows:
        print("Sin datos.")
        return
    current_tid = None
    for r in rows:
        (
            tid,
            estado,
            diag,
            medico,
            ses_est,
            eficacia,
            cita_id,
            fecha,
            tipo,
            pagado,
            nota,
        ) = r
        if tid != current_tid:
            current_tid = tid
            print("\n" + "=" * 50)
            line = f"TRATAMIENTO #{tid} - {estado}"
            print(line)
            print(f"Diagnóstico: {diag}")
            print(f"Médico: {medico} | Sesiones Est.: {ses_est}")
            if eficacia is not None:
                print(f"Eficacia Lograda: {eficacia}%")
            print("-" * 50)
        if cita_id is None:
            continue
        marca = "[X]" if pagado else "[P]"
        nota_s = nota if nota else "None"
        print(f"  {marca} {fecha} | {tipo} | {nota_s}")


def modulo_consultas(conn) -> None:
    while True:
        print("\n[1] Lista de Pacientes | [2] Deudas de Paciente | [3] Historial Clínico | [4] Tratamientos por Paciente")
        op = prompt_int("Acción: ", min_v=1, max_v=4)
        if op is None:
            continue
        try:
            with conn.cursor() as cur:
                if op == 1:
                    rows = repo.listar_pacientes(cur)
                    print()
                    print_pacientes_table(rows)
                elif op == 2:
                    pid = prompt_int("Ingrese el ID del paciente: ", min_v=1)
                    if pid is None:
                        continue
                    deudas = repo.deudas_paciente(cur, pid)
                    if not deudas:
                        print("El paciente no tiene citas pendientes de pago.")
                    else:
                        for d in deudas:
                            cid, fh, tipo, monto, tid, diagnostico = d
                            print(f"  Cita {cid} | Trat. {tid} | {fh} | {tipo} | ${monto} | {diagnostico}")
                elif op == 3:
                    pid = prompt_int("Ingrese el ID del paciente: ", min_v=1)
                    if pid is None:
                        continue
                    rows = repo.historial_clinico(cur, pid)
                    mostrar_historial(rows)
                else:
                    pid = prompt_int("Ingrese el ID del paciente: ", min_v=1)
                    if pid is None:
                        continue
                    rows = repo.tratamientos_por_paciente(cur, pid)
                    for r in rows:
                        tid, est, diag, med, sest, efic, n_citas = r
                        print(f"\n--- Tratamiento #{tid} ({est}) ---")
                        print(f"  {diag} | {med} | Estimadas: {sest} | Citas: {n_citas}")
                        if efic is not None:
                            print(f"  Eficacia: {efic}%")
        except psycopg2.Error as e:
            print(format_db_error(e))
        return


def print_organigrama_arbol(rows: list[tuple]) -> None:
    """Árbol por supervisor_id (misma jerarquía que la CTE v_organigrama)."""
    by_sup: dict[Optional[int], list[tuple]] = defaultdict(list)
    for eid, nom, esp, sup, _rol in rows:
        by_sup[sup].append((eid, nom, esp))
    for k in by_sup:
        by_sup[k].sort(key=lambda x: x[1])

    def walk(parent_id: Optional[int], nivel: int) -> None:
        for eid, nom, esp in by_sup.get(parent_id, []):
            indent = "  " * nivel
            print(f"{indent}└─ {nom} (ID: {esp})")
            walk(eid, nivel + 1)

    walk(None, 0)


def modulo_gerencia(conn) -> None:
    while True:
        print("\n[1] Organigrama | [2] Reporte de Adherencia | [3] Cadena de Referidos")
        op = prompt_int("Acción: ", min_v=1, max_v=3)
        if op is None:
            continue
        try:
            with conn.cursor() as cur:
                if op == 1:
                    rows = repo.organigrama_empleados(cur)
                    print_organigrama_arbol(rows)
                elif op == 2:
                    banner("ANALÍTICA: REPORTE DE ADHERENCIA AL TRATAMIENTO")
                    rows = repo.reporte_adherencia(cur)
                    print(f"{'PACIENTE':<25} {'PROM. DÍAS ENTRE CITAS':<22} {'ESTADO ADHERENCIA':<30}")
                    print("-" * 80)
                    for nombre, prom, estado in rows:
                        print(f"{str(nombre)[:25]:<25} {str(prom):<22} {estado:<30}")
                else:
                    rows = repo.cadena_referidos(cur)
                    print("CADENA DE REFERIDOS (vista recursiva)")
                    print("-" * 60)
                    for _pid, nombre, nivel, cadena in rows:
                        print(f"[nivel {nivel}] {nombre}: {cadena}")
        except psycopg2.Error as e:
            print(format_db_error(e))
        return


def main_menu(conn) -> None:
    while True:
        banner("SISTEMA ORTHOCONNECT v1.0")
        print("1. Módulo Administrativo (Creación de Pacientes, Tratamientos, Citas y Pagos)")
        print("2. Módulo Médico (Evolución de cita y Cierre de tratamiento)")
        print("3. Módulo de Consultas (Pacientes e Historias)")
        print("4. Módulo Gerencial (Analítica y Jerarquía)")
        print("5. Salir")
        op = prompt_int("\nSeleccione una opción: ", min_v=1, max_v=5)
        if op is None:
            continue
        if op == 5:
            print("Hasta luego.")
            return
        if op == 1:
            modulo_administrativo(conn)
        elif op == 2:
            modulo_medico(conn)
        elif op == 3:
            modulo_consultas(conn)
        elif op == 4:
            modulo_gerencia(conn)


def main() -> int:
    print("Conexión a PostgreSQL (variables PG* en .env o entorno).")
    app_user = prompt_line("Nombre del operador (auditoría / application_name): ") or "cli"
    try:
        conn = connect()
    except psycopg2.Error as e:
        print("No se pudo conectar:", e)
        return 1
    try:
        set_application_name(conn, app_user)
        conn.commit()
        main_menu(conn)
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
