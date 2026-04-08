"""Validaciones end-to-end contra PostgreSQL real."""
from __future__ import annotations

import unittest
from pathlib import Path

import psycopg2

from tests.pg_util import pg_available


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_SQL = ROOT / "sql" / "schema.sql"
SEED_SQL = ROOT / "sql" / "seed.sql"


@unittest.skipUnless(pg_available(), "PostgreSQL no disponible (configurar .env o ORTHCONNECT_SKIP_PG_TESTS=1)")
class PostgresRepoSmokeTest(unittest.TestCase):
    @staticmethod
    def _reset_db(conn) -> None:
        with conn.cursor() as cur:
            cur.execute(SCHEMA_SQL.read_text())
            cur.execute(SEED_SQL.read_text())
        conn.commit()

    def setUp(self) -> None:
        from src.db import connect, set_application_name

        self.conn = connect()
        self._reset_db(self.conn)
        set_application_name(self.conn, "pg_test")
        self.conn.commit()

    def tearDown(self) -> None:
        self.conn.close()

    def test_listar_y_vistas(self) -> None:
        from src import repo as repo_pg

        with self.conn.cursor() as cur:
            self.assertGreaterEqual(len(repo_pg.listar_pacientes(cur)), 1)
            self.assertGreaterEqual(len(repo_pg.listar_tratamientos(cur)), 1)
            self.assertGreaterEqual(len(repo_pg.organigrama_empleados(cur)), 1)
            self.assertGreaterEqual(len(repo_pg.reporte_adherencia(cur)), 1)
            self.assertGreaterEqual(len(repo_pg.cadena_referidos(cur)), 1)
            self.assertGreaterEqual(len(repo_pg.reporte_eficacia(cur)), 1)

    def test_morosidad_bloquea_tercera_cita_anterior(self) -> None:
        from datetime import datetime
        from decimal import Decimal

        from src import repo as repo_pg

        with self.conn.cursor() as cur:
            with self.assertRaises(psycopg2.Error) as ctx:
                repo_pg.insertar_cita(
                    cur,
                    1,
                    datetime(2026, 3, 25, 10, 0),
                    "Sesion control",
                    Decimal("50000"),
                    3,
                )
        self.conn.rollback()
        self.assertIn("BLOQUEO", str(ctx.exception))

    def test_aplicar_pago_registra_pago_fifo(self) -> None:
        from src import repo as repo_pg

        with self.conn.cursor() as cur:
            row = repo_pg.aplicar_pago(cur, 1)
            self.assertIsNotNone(row)
            pago_id, cita_id, _fecha, _tipo, monto = row
            self.assertEqual(cita_id, 1)
            self.assertEqual(str(monto), "80000.00")

            cur.execute(
                """
                SELECT tratamiento_id, cita_id_saldada, usuario_registro
                FROM pago
                WHERE pago_id = %s
                """,
                (pago_id,),
            )
            pago = cur.fetchone()
            self.assertEqual(pago, (1, 1, "pg_test"))

    def test_actualizar_evolucion_audita_y_asiste(self) -> None:
        from src import repo as repo_pg

        with self.conn.cursor() as cur:
            updated = repo_pg.actualizar_evolucion(cur, 3, "Paciente completa sesion sin dolor.")
            self.assertEqual(updated, 1)
            cur.execute(
                """
                SELECT estado_asistencia, nota_evolucion
                FROM cita
                WHERE cita_id = 3
                """
            )
            self.assertEqual(cur.fetchone(), ("ASISTIDA", "Paciente completa sesion sin dolor."))
            cur.execute(
                """
                SELECT nota_anterior, nota_nueva, usuario_editor
                FROM auditoria_evolucion
                WHERE cita_id = 3
                ORDER BY auditoria_id DESC
                LIMIT 1
                """
            )
            audit = cur.fetchone()
            self.assertEqual(audit, (None, "Paciente completa sesion sin dolor.", "pg_test"))

    def test_finalizar_tratamiento_calcula_eficacia_por_asistencia(self) -> None:
        from src import repo as repo_pg

        with self.conn.cursor() as cur:
            repo_pg.actualizar_evolucion(cur, 3, "Paciente completa sesion sin dolor.")
            row = repo_pg.finalizar_tratamiento(cur, 1)
            self.assertEqual(row[1], "FINALIZADO")
            self.assertEqual(str(row[2]), "500.00")


if __name__ == "__main__":
    unittest.main()
