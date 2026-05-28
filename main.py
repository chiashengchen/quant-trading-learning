from FinMind.data import DataLoader
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

api = DataLoader()

df = api.taiwan_stock_daily(
    stock_id="2330",
    start_date="2015-01-01",
    end_date="2025-01-01"
)

print(df.head())
print(df.columns)
