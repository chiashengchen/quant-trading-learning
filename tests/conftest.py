"""
Shared fixtures for all tests.

Key design: patch database.get_connection to return an in-memory SQLite
connection so tests never touch the real DB file.
"""
import sqlite3
import pandas as pd
import pytest


@pytest.fixture
def in_memory_conn():
    """A fresh in-memory SQLite connection with the schema initialised."""
    conn = sqlite3.connect(":memory:")
    conn.execute(
        """
        CREATE TABLE daily_prices (
            stock_id TEXT NOT NULL,
            date TEXT NOT NULL,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume REAL,
            trading_money REAL,
            spread REAL,
            transactions REAL,
            PRIMARY KEY (stock_id, date)
        )
        """
    )
    conn.commit()
    yield conn
    conn.close()


class _NoCloseConn:
    """Proxy that prevents production code from closing our shared in-memory connection."""

    def __init__(self, conn):
        self._conn = conn

    def close(self):
        pass  # intentionally a no-op

    def __getattr__(self, name):
        return getattr(self._conn, name)


@pytest.fixture
def patch_db(in_memory_conn, monkeypatch):
    """
    Redirect every get_connection() call in database / repositories to the
    shared in-memory connection so no file I/O happens during tests.

    The connection is wrapped to ignore .close() calls because production
    functions close the connection at the end of each operation.
    """
    import database
    import repositories

    proxy = _NoCloseConn(in_memory_conn)
    monkeypatch.setattr(database, "get_connection", lambda: proxy)
    monkeypatch.setattr(repositories, "get_connection", lambda: proxy)
    return in_memory_conn


@pytest.fixture
def sample_price_df():
    """Minimal price DataFrame that matches what load_stock_data returns."""
    dates = pd.date_range("2024-01-02", periods=5, freq="B")
    return pd.DataFrame(
        {
            "open":  [100.0, 101.0, 102.0, 101.5, 103.0],
            "high":  [101.0, 102.0, 103.0, 102.5, 104.0],
            "low":   [ 99.0, 100.0, 101.0, 100.5, 102.0],
            "close": [100.5, 101.5, 102.5, 101.0, 103.5],
            "volume": [1000.0, 1200.0, 900.0, 1100.0, 1300.0],
        },
        index=pd.Index(dates, name="date"),
    )
