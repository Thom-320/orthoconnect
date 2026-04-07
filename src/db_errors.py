"""Formateo de errores de PostgreSQL para el usuario."""

import re

import psycopg2


def format_db_error(exc: BaseException) -> str:
    if not isinstance(exc, psycopg2.Error):
        return str(exc)

    parts: list[str] = []
    diag = getattr(exc, "diag", None)
    primary = getattr(diag, "message_primary", None) if diag else None
    context = getattr(diag, "context", None) if diag else None

    if primary:
        if primary.startswith("BLOQUEO:"):
            parts.append("REGLA DE NEGOCIO VIOLADA: " + primary)
        elif "INFO:NO_HAY_DEUDAS:" in primary:
            msg = primary.split("INFO:NO_HAY_DEUDAS:", 1)[-1].strip()
            parts.append(msg)
        else:
            parts.append(primary)
    else:
        parts.append(str(exc).strip())

    if context and "CONTEXT:" not in "\n".join(parts):
        ctx_one_line = re.sub(r"\s+", " ", context.strip())
        parts.append("CONTEXT: " + ctx_one_line)

    return "\n".join(parts)


def is_business_rule_violation(exc: BaseException) -> bool:
    if not isinstance(exc, psycopg2.Error):
        return False
    diag = getattr(exc, "diag", None)
    primary = (getattr(diag, "message_primary", None) or "").upper()
    return primary.startswith("BLOQUEO:") or "INFO:NO_HAY_DEUDAS:" in primary
