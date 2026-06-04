import pandas as pd

from database import get_connection


def save_daily_prices(stock_id, df):
    conn = get_connection()

    df = df.copy()
    df = df.reset_index()

    records = []

    for _, row in df.iterrows():
        records.append({
            "stock_id": stock_id,
            "date": row["date"].strftime("%Y-%m-%d"),
            "open": row.get("open"),
            "high": row.get("max", row.get("high")),
            "low": row.get("min", row.get("low")),
            "close": row.get("close"),
            "volume": row.get("Trading_Volume", row.get("volume")),
            "trading_money": row.get("Trading_money", row.get("trading_money")),
            "spread": row.get("spread"),
            "transactions": row.get("Trading_turnover", row.get("transactions")),
        })

    insert_df = pd.DataFrame(records)

    insert_df.to_sql(
        "daily_prices_temp",
        conn,
        if_exists="replace",
        index=False,
    )

    conn.execute(
        """
        INSERT OR REPLACE INTO daily_prices (
            stock_id,
            date,
            open,
            high,
            low,
            close,
            volume,
            trading_money,
            spread,
            transactions
        )
        SELECT
            stock_id,
            date,
            open,
            high,
            low,
            close,
            volume,
            trading_money,
            spread,
            transactions
        FROM daily_prices_temp
        """
    )

    conn.execute("DROP TABLE daily_prices_temp")
    conn.commit()
    conn.close()


def load_daily_prices(stock_id, start_date=None, end_date=None):
    conn = get_connection()

    query = """
        SELECT
            date,
            open,
            high,
            low,
            close,
            volume,
            trading_money,
            spread,
            transactions
        FROM daily_prices
        WHERE stock_id = ?
    """

    params = [stock_id]

    if start_date is not None:
        query += " AND date >= ?"
        params.append(start_date)

    if end_date is not None:
        query += " AND date <= ?"
        params.append(end_date)

    query += " ORDER BY date"

    df = pd.read_sql_query(query, conn, params=params)
    conn.close()

    if df.empty:
        return df

    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date")

    return df


def get_latest_price_date(stock_id):
    conn = get_connection()

    query = """
        SELECT MAX(date) AS latest_date
        FROM daily_prices
        WHERE stock_id = ?
    """

    df = pd.read_sql_query(query, conn, params=[stock_id])
    conn.close()

    return df.loc[0, "latest_date"]