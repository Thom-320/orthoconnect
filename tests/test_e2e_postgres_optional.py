"""PostgreSQL opcional: se omite si no hay conexión o variables."""
from __future__ import annotations

import os
import unittest

try:
    import psycopg2
except ImportError:
    psycopg2 = None  # type: ignore


def _pg_available() -> bool:
    if psycopg2 is None:
        return False
    if os.environ.get("ORTHCONNECT_SKIP_PG_TESTS", "").lower() in ("1", "true", "yes"):
        return False
    try:
        from src.db import connect

        conn = connect()
        conn.close()
        return True
    except Exception:
        return False


@unittest.skipUnless(_pg_available(), "PostgreSQL no disponible (omitir o configurar .env)")
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
