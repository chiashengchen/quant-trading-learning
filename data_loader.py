import numpy as np
import pandas as pd
from FinMind.data import DataLoader


def load_stock_data(stock_id, start_date, end_date):
    api = DataLoader()

    df = api.taiwan_stock_daily(
        stock_id=stock_id,
        start_date=start_date,
        end_date=end_date,
    )

    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")
    df = df.set_index("date")

    return df


def build_raw_close_table(data, price_col="close"):
    close_table = pd.DataFrame()

    for stock_id, df in data.items():
        if df.empty:
            continue

        close_table[stock_id] = df[price_col]

    close_table = close_table.sort_index()

    return close_table


def build_clean_close_table(data, price_col="close"):
    close_table = build_raw_close_table(data, price_col=price_col)

    close_table = close_table.replace(0, np.nan)
    close_table = close_table.mask(close_table < 0, np.nan)

    close_table = close_table.dropna()

    return close_table


def build_price_and_tradable_tables(data, price_col="close"):
    """
    進階版：
    price_table: 用 ffill 做估值
    tradable_table: 判斷當天是否可交易

    注意：
    ffill 可以用於 valuation，但不應該拿來假裝當天可以成交。
    """
    raw_close_table = build_raw_close_table(data, price_col=price_col)

    raw = raw_close_table.copy()
    raw = raw.replace(0, np.nan)
    raw = raw.mask(raw < 0, np.nan)

    tradable_table = raw.notna()

    price_table = raw.ffill()

    # 移除最前面仍有缺值的日期
    valid_index = price_table.dropna().index
    price_table = price_table.loc[valid_index]
    tradable_table = tradable_table.loc[valid_index]

    return price_table, tradable_table