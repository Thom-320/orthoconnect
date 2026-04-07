"""Smoke del CLI (rich) con entrada simulada — sin abrir GUI."""
from __future__ import annotations

import unittest
from unittest.mock import patch


class CliDemoSmokeTest(unittest.TestCase):
    def test_demo_flow_exits_zero(self) -> None:
        inputs = [
            "1",
            "cli_e2e",
            "3",
            "1",
            "5",
            "4",
            "2",
            "4",
            "5",
            "5",
        ]
        inp = iter(inputs)

        with patch("builtins.input", lambda *a, **k: next(inp)):
            from src.main import main

            code = main()
        self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
