import sqlite3
from config import DB_PATH


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS daily_prices (
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
    conn.close()