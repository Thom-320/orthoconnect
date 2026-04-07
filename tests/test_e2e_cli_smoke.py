"""Smoke del CLI: conexión PostgreSQL y salida limpia (requiere BD)."""
from __future__ import annotations

import unittest
from unittest.mock import patch

from tests.pg_util import pg_available


@unittest.skipUnless(pg_available(), "PostgreSQL no disponible (configurar .env o omitir con ORTHCONNECT_SKIP_PG_TESTS=1)")
class CliPgSmokeTest(unittest.TestCase):
    def test_connect_operator_and_exit(self) -> None:
        inputs = [
            "cli_smoke",
            "5",
        ]
        inp = iter(inputs)

        with patch("builtins.input", lambda *a, **k: next(inp)):
            from src.main import main

            code = main()
        self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
