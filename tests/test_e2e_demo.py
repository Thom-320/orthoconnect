"""
E2E lógico en modo Demo: mismas rutas que usa la GUI/CLI sin PostgreSQL.
"""
from __future__ import annotations

import unittest
from datetime import datetime
from decimal import Decimal

from src import repo_demo


class DemoRepoGuiPathsTest(unittest.TestCase):
    """Todas las llamadas que hace gui_main sobre el cursor."""

    def setUp(self) -> None:
        self.conn = repo_demo.DemoConnection()
        self.conn.data.app_user = "e2e_test"
        self.repo = repo_demo

    def test_listar_pacientes_tratamientos_medicos(self) -> None:
        with self.conn.cursor() as cur:
            p = self.repo.listar_pacientes(cur)
            self.assertGreaterEqual(len(p), 1)
            t = self.repo.listar_tratamientos(cur)
            self.assertGreaterEqual(len(t), 1)
            m = self.repo.listar_medicos_tratantes(cur)
            self.assertGreaterEqual(len(m), 1)

    def test_insertar_paciente_y_tratamiento(self) -> None:
        with self.conn.cursor() as cur:
            pid = self.repo.insertar_paciente(cur, "E2E User", "1995-01-01", "3000000000", None)
            self.assertGreater(pid, 0)
            tid = self.repo.insertar_tratamiento(cur, pid, 1, "Test dx", 5)
            self.assertGreater(tid, 0)

    def test_tratamiento_existe_insertar_cita(self) -> None:
        # Tratamiento 3 (paciente al día en seed); el 1 tiene 2 pendientes → bloquearía morosidad.
        with self.conn.cursor() as cur:
            self.assertTrue(self.repo.tratamiento_existe(cur, 3))
            cid = self.repo.insertar_cita(
                cur, 3, datetime(2026, 6, 1, 10, 0), "E2E", Decimal("1000"), None
            )
            self.assertGreater(cid, 0)

    def test_morosidad_bloquea_agenda(self) -> None:
        with self.conn.cursor() as cur:
            with self.assertRaises(ValueError) as ctx:
                self.repo.insertar_cita(
                    cur, 1, datetime(2026, 6, 2, 10, 0), "E2E", Decimal("1000"), None
                )
            self.assertIn("BLOQUEO", str(ctx.exception))

    def test_aplicar_pago(self) -> None:
        with self.conn.cursor() as cur:
            row = self.repo.aplicar_pago(cur, 1)
            self.assertIsNotNone(row)
            self.assertEqual(len(row), 5)

    def test_evolucion_y_finalizar(self) -> None:
        with self.conn.cursor() as cur:
            self.assertTrue(self.repo.cita_existe(cur, 2))
            n = self.repo.actualizar_evolucion(cur, 2, "Nota E2E")
            self.assertEqual(n, 1)
            row = self.repo.finalizar_tratamiento(cur, 3)
            self.assertEqual(len(row), 4)

    def test_reportes_gerencia(self) -> None:
        with self.conn.cursor() as cur:
            o = self.repo.organigrama_empleados(cur)
            self.assertGreaterEqual(len(o), 1)
            a = self.repo.reporte_adherencia(cur)
            self.assertIsInstance(a, list)
            r = self.repo.cadena_referidos(cur)
            self.assertGreaterEqual(len(r), 1)

    def test_demo_cursor_rejects_raw_sql(self) -> None:
        with self.conn.cursor() as cur:
            with self.assertRaises(RuntimeError) as ctx:
                cur.execute("SELECT 1")
            self.assertIn("repo_demo", str(ctx.exception))


class GuiRepoRoutingTest(unittest.TestCase):
    def test_effective_repo_for_connection(self) -> None:
        from src import repo as repo_pg
        from src import repo_demo

        try:
            from src.gui_main import effective_repo_for_connection
        except ModuleNotFoundError as exc:
            self.skipTest(f"GUI opcional no disponible en este entorno: {exc}")

        conn = repo_demo.DemoConnection()
        self.assertIs(effective_repo_for_connection(conn, repo_pg), repo_demo)
        # PostgreSQL: se respeta el módulo pasado (mock con tipo distinto)
        class _FakeConn:
            pass

        self.assertIs(effective_repo_for_connection(_FakeConn(), repo_pg), repo_pg)


if __name__ == "__main__":
    unittest.main()
