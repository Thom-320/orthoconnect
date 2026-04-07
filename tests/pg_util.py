"""Utilidad compartida: ¿hay PostgreSQL según .env / src.db?"""
from __future__ import annotations

import os


def pg_available() -> bool:
    if os.environ.get("ORTHCONNECT_SKIP_PG_TESTS", "").lower() in ("1", "true", "yes"):
        return False
    try:
        from src.db import connect

        conn = connect()
        conn.close()
        return True
    except Exception:
        return False
