import threading
from pathlib import Path

import duckdb

from market_pulse.config import settings

_local = threading.local()
_MIGRATIONS_DIR = Path(__file__).parent / "migrations"


def get_connection(db_path: Path | None = None) -> duckdb.DuckDBPyConnection:
    """Return a thread-local DuckDB connection, creating it if needed."""
    path = db_path or settings.db_path
    if not hasattr(_local, "conn") or _local.conn is None:
        path.parent.mkdir(parents=True, exist_ok=True)
        _local.conn = duckdb.connect(str(path))
        _run_migrations(_local.conn)
    return _local.conn  # type: ignore[return-value]


def get_memory_connection() -> duckdb.DuckDBPyConnection:
    """In-memory connection for testing."""
    conn = duckdb.connect(":memory:")
    _run_migrations(conn)
    return conn


def _run_migrations(conn: duckdb.DuckDBPyConnection) -> None:
    for sql_file in sorted(_MIGRATIONS_DIR.glob("*.sql")):
        conn.execute(sql_file.read_text())


def close_connection() -> None:
    if hasattr(_local, "conn") and _local.conn is not None:
        _local.conn.close()
        _local.conn = None
