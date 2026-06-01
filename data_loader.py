from FinMind.data import DataLoader
import pandas as pd
import numpy as np


def load_stock_data(stock_id, start_date, end_date):
    api = DataLoader()

    df = api.taiwan_stock_daily(
        stock_id=stock_id,
        start_date=start_date,
        end_date=end_date
    )

    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")
    df = df.set_index("date")

    return df


def load_multiple_stocks(stock_ids, start_date, end_date):
    data = {}

    for stock_id in stock_ids:
        data[stock_id] = load_stock_data(stock_id, start_date, end_date)

    return data


def build_close_table(data):
    close_table = pd.DataFrame()

    for stock_id, df in data.items():
        close_table[stock_id] = df["close"]

    close_table = close_table.sort_index()

    # 0 價格不合理，先視為缺值
    close_table = close_table.replace(0, np.nan)

    # 用前一天價格補值
    close_table = close_table.ffill()

    # 移除最前面仍然缺資料的 row
    close_table = close_table.dropna()

    return close_table