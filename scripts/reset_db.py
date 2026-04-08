"""Recarga schema.sql y seed.sql sobre la base configurada en .env."""

from pathlib import Path

from src.db import connect


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "sql" / "schema.sql"
SEED = ROOT / "sql" / "seed.sql"


def main() -> int:
    conn = connect()
    try:
        with conn.cursor() as cur:
            cur.execute(SCHEMA.read_text())
            cur.execute(SEED.read_text())
        conn.commit()
        print("Base recargada con schema.sql y seed.sql")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
