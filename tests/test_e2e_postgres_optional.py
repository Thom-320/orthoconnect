"""Consultas reales al repositorio contra PostgreSQL."""
from __future__ import annotations

import unittest

from tests.pg_util import pg_available


@unittest.skipUnless(pg_available(), "PostgreSQL no disponible (configurar .env o ORTHCONNECT_SKIP_PG_TESTS=1)")
class PostgresRepoSmokeTest(unittest.TestCase):
    def test_listar_y_vistas(self) -> None:
        from src.db import connect
        from src import repo as repo_pg

        conn = connect()
        try:
            with conn.cursor() as cur:
                p = repo_pg.listar_pacientes(cur)
                self.assertIsInstance(p, list)
                t = repo_pg.listar_tratamientos(cur)
                self.assertIsInstance(t, list)
                o = repo_pg.organigrama_empleados(cur)
                self.assertIsInstance(o, list)
                a = repo_pg.reporte_adherencia(cur)
                self.assertIsInstance(a, list)
                r = repo_pg.cadena_referidos(cur)
                self.assertIsInstance(r, list)
        finally:
            conn.close()


if __name__ == "__main__":
    unittest.main()
