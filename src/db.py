"""Conexión PostgreSQL vía variables de entorno."""

import os
from contextlib import contextmanager

import psycopg2
from dotenv import load_dotenv


def connect():
    load_dotenv()
    user = os.getenv("PGUSER") or os.environ.get("USER") or "postgres"
    return psycopg2.connect(
        host=os.getenv("PGHOST", "localhost"),
        port=os.getenv("PGPORT", "5432"),
        dbname=os.getenv("PGDATABASE", "orthoconnect"),
        user=user,
        password=os.getenv("PGPASSWORD", ""),
    )


def set_application_name(conn, name: str) -> None:
    """Usado por triggers de auditoría (current_setting('application_name'))."""
    safe = (name or "cli").replace("\x00", "")[:200]
    with conn.cursor() as cur:
        cur.execute("SET application_name TO %s", (safe,))


@contextmanager
def transaction(conn):
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
