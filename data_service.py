from datetime import datetime, timedelta

from data_loader import (
    load_stock_data,
    build_clean_close_table,
    build_price_and_tradable_tables,
)

from database import (
    init_db,
    save_daily_prices,
    load_daily_prices_from_db,
    get_latest_price_date,
)


def fetch_and_store_stock_data(stock_id, start_date, end_date):
    """
    Fetch stock daily price data from FinMind API and save it into SQLite.

    Args:
        stock_id (str): Taiwan stock id, e.g. "0050", "2330".
        start_date (str): YYYY-MM-DD.
        end_date (str): YYYY-MM-DD.

    Returns:
        pd.DataFrame: Fetched stock data.
    """
    df = load_stock_data(
        stock_id=stock_id,
        start_date=start_date,
        end_date=end_date,
    )

    if df.empty:
        print(f"No data fetched for {stock_id}")
        return df

    save_daily_prices(stock_id, df)

    print(f"Saved {len(df)} rows for {stock_id} into DB.")

    return df


def load_or_fetch_stock_data(stock_id, start_date, end_date):
    """
    Load stock data from DB first.
    If DB has no data in the requested range, fetch from API and store into DB.

    Args:
        stock_id (str): Taiwan stock id.
        start_date (str): YYYY-MM-DD.
        end_date (str): YYYY-MM-DD.

    Returns:
        pd.DataFrame: Stock daily price data indexed by date.
    """
    init_db()

    db_df = load_daily_prices_from_db(
        stock_id=stock_id,
        start_date=start_date,
        end_date=end_date,
    )

    if not db_df.empty:
        print(f"Loaded {stock_id} from DB.")
        return db_df

    print(f"No DB data for {stock_id}. Fetching from API...")

    fetch_and_store_stock_data(
        stock_id=stock_id,
        start_date=start_date,
        end_date=end_date,
    )

    return load_daily_prices_from_db(
        stock_id=stock_id,
        start_date=start_date,
        end_date=end_date,
    )


def update_stock_data(stock_id, start_date, end_date):
    """
    Incrementally update stock data.

    Logic:
    - If no data exists in DB, fetch from start_date.
    - If data exists, fetch from latest_date + 1 day.
    - If already up to date, just return DB data.

    Args:
        stock_id (str): Taiwan stock id.
        start_date (str): YYYY-MM-DD.
        end_date (str): YYYY-MM-DD.

    Returns:
        pd.DataFrame: Stock daily price data indexed by date.
    """
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

        return load_daily_prices_from_db(
            stock_id=stock_id,
            start_date=start_date,
            end_date=end_date,
        )

    fetch_and_store_stock_data(
        stock_id=stock_id,
        start_date=fetch_start,
        end_date=end_date,
    )

    return load_daily_prices_from_db(
        stock_id=stock_id,
        start_date=start_date,
        end_date=end_date,
    )


def load_or_fetch_multiple_stocks(stock_ids, start_date, end_date):
    """
    Load multiple stocks from DB.
    If a stock has no DB data, fetch from API and store into DB.

    Args:
        stock_ids (list[str]): List of Taiwan stock ids.
        start_date (str): YYYY-MM-DD.
        end_date (str): YYYY-MM-DD.

    Returns:
        dict[str, pd.DataFrame]: Mapping stock_id -> price dataframe.
    """
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
    """
    Incrementally update multiple stocks.

    Args:
        stock_ids (list[str]): List of Taiwan stock ids.
        start_date (str): YYYY-MM-DD.
        end_date (str): YYYY-MM-DD.

    Returns:
        dict[str, pd.DataFrame]: Mapping stock_id -> updated price dataframe.
    """
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


def load_or_fetch_close_table(
    stock_ids,
    start_date,
    end_date,
    price_col="close",
):
    """
    Load multiple stocks and build a clean close table.

    This is useful for portfolio strategies.

    Args:
        stock_ids (list[str]): List of Taiwan stock ids.
        start_date (str): YYYY-MM-DD.
        end_date (str): YYYY-MM-DD.
        price_col (str): Price column to use, usually "close".

    Returns:
        pd.DataFrame: Clean close table.
    """
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


def update_close_table(
    stock_ids,
    start_date,
    end_date,
    price_col="close",
):
    """
    Incrementally update multiple stocks and build a clean close table.

    Args:
        stock_ids (list[str]): List of Taiwan stock ids.
        start_date (str): YYYY-MM-DD.
        end_date (str): YYYY-MM-DD.
        price_col (str): Price column to use.

    Returns:
        pd.DataFrame: Clean close table.
    """
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


def load_or_fetch_price_and_tradable_tables(
    stock_ids,
    start_date,
    end_date,
    price_col="close",
):
    """
    Load multiple stocks and build:
    - price_table: can be used for valuation
    - tradable_table: tells whether each stock is tradable on each day

    Note:
    price_table may use ffill for valuation.
    tradable_table should be used to avoid pretending untradable stocks can be traded.

    Args:
        stock_ids (list[str]): List of Taiwan stock ids.
        start_date (str): YYYY-MM-DD.
        end_date (str): YYYY-MM-DD.
        price_col (str): Price column to use.

    Returns:
        tuple[pd.DataFrame, pd.DataFrame]: price_table, tradable_table
    """
    data = load_or_fetch_multiple_stocks(
        stock_ids=stock_ids,
        start_date=start_date,
        end_date=end_date,
    )

    price_table, tradable_table = build_price_and_tradable_tables(
        data,
        price_col=price_col,
    )

    return price_table, tradable_table


def update_price_and_tradable_tables(
    stock_ids,
    start_date,
    end_date,
    price_col="close",
):
    """
    Incrementally update multiple stocks and build:
    - price_table
    - tradable_table

    Args:
        stock_ids (list[str]): List of Taiwan stock ids.
        start_date (str): YYYY-MM-DD.
        end_date (str): YYYY-MM-DD.
        price_col (str): Price column to use.

    Returns:
        tuple[pd.DataFrame, pd.DataFrame]: price_table, tradable_table
    """
    data = update_multiple_stocks(
        stock_ids=stock_ids,
        start_date=start_date,
        end_date=end_date,
    )

    price_table, tradable_table = build_price_and_tradable_tables(
        data,
        price_col=price_col,
    )

    return price_table, tradable_table