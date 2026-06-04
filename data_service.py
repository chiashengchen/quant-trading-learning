from datetime import datetime, timedelta

from database import init_db
from data_loader import load_stock_data
from repositories import (
    save_daily_prices,
    load_daily_prices,
    get_latest_price_date,
)


def fetch_and_store_stock_data(stock_id, start_date, end_date):
    df = load_stock_data(stock_id, start_date, end_date)

    if df.empty:
        print(f"No data fetched for {stock_id}")
        return df

    save_daily_prices(stock_id, df)

    return df


def get_daily_prices(stock_id, start_date, end_date, auto_fetch=True):
    init_db()

    df = load_daily_prices(stock_id, start_date, end_date)

    if not df.empty:
        return df

    if not auto_fetch:
        return df

    print(f"No DB data for {stock_id}. Fetching from API...")

    fetch_and_store_stock_data(stock_id, start_date, end_date)

    return load_daily_prices(stock_id, start_date, end_date)


def update_daily_prices(stock_id, start_date, end_date):
    init_db()

    latest_date = get_latest_price_date(stock_id)

    if latest_date is None:
        fetch_start = start_date
        print(f"No existing data for {stock_id}. Fetching from {fetch_start}...")
    else:
        latest_dt = datetime.strptime(latest_date, "%Y-%m-%d")
        fetch_start = (latest_dt + timedelta(days=1)).strftime("%Y-%m-%d")

        print(f"Latest data for {stock_id}: {latest_date}")
        print(f"Fetching from {fetch_start}...")

    if fetch_start > end_date:
        print(f"{stock_id} is already up to date.")
        return load_daily_prices(stock_id, start_date, end_date)

    fetch_and_store_stock_data(stock_id, fetch_start, end_date)

    return load_daily_prices(stock_id, start_date, end_date)