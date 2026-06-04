from datetime import datetime, timedelta

from data_loader import load_stock_data, build_clean_close_table
from database import (
    init_db,
    save_daily_prices,
    load_daily_prices_from_db,
    get_latest_price_date,
)


def fetch_and_store_stock_data(stock_id, start_date, end_date):
    df = load_stock_data(stock_id, start_date, end_date)

    if df.empty:
        print(f"No data fetched for {stock_id}")
        return df

    save_daily_prices(stock_id, df)

    print(f"Saved {len(df)} rows for {stock_id} into DB.")

    return df


def load_or_fetch_stock_data(stock_id, start_date, end_date):
    init_db()

    db_df = load_daily_prices_from_db(stock_id, start_date, end_date)

    if not db_df.empty:
        print(f"Loaded {stock_id} from DB.")
        return db_df

    print(f"No DB data for {stock_id}. Fetching from API...")

    fetch_and_store_stock_data(stock_id, start_date, end_date)

    return load_daily_prices_from_db(stock_id, start_date, end_date)


def update_stock_data(stock_id, start_date, end_date):
    init_db()

    latest_date = get_latest_price_date(stock_id)

    if latest_date is None:
        print(f"No existing data for {stock_id}. Fetching from {start_date}...")
        fetch_start = start_date
    else:
        latest_dt = datetime.strptime(latest_date, "%Y-%m-%d")
        fetch_start = (latest_dt + timedelta(days=1)).strftime("%Y-%m-%d")

        print(f"Latest data for {stock_id}: {latest_date}")
        print(f"Fetching from {fetch_start}...")

    if fetch_start > end_date:
        print(f"{stock_id} is already up to date.")
        return load_daily_prices_from_db(stock_id, start_date, end_date)

    fetch_and_store_stock_data(stock_id, fetch_start, end_date)

    return load_daily_prices_from_db(stock_id, start_date, end_date)


def load_or_fetch_multiple_stocks(stock_ids, start_date, end_date):
    data = {}

    for stock_id in stock_ids:
        print(f"\nLoading {stock_id}")

        df = load_or_fetch_stock_data(
            stock_id=stock_id,
            start_date=start_date,
            end_date=end_date,
        )

        data[stock_id] = df

    return data


def update_multiple_stocks(stock_ids, start_date, end_date):
    data = {}

    for stock_id in stock_ids:
        print(f"\nUpdating {stock_id}")

        df = update_stock_data(
            stock_id=stock_id,
            start_date=start_date,
            end_date=end_date,
        )

        data[stock_id] = df

    return data


def load_or_fetch_close_table(stock_ids, start_date, end_date, price_col="close"):
    data = load_or_fetch_multiple_stocks(
        stock_ids=stock_ids,
        start_date=start_date,
        end_date=end_date,
    )

    close_table = build_clean_close_table(
        data,
        price_col=price_col,
    )

    return close_table


def update_close_table(stock_ids, start_date, end_date, price_col="close"):
    data = update_multiple_stocks(
        stock_ids=stock_ids,
        start_date=start_date,
        end_date=end_date,
    )

    close_table = build_clean_close_table(
        data,
        price_col=price_col,
    )

    return close_table