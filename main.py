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

df["date"] = pd.to_datetime(df["date"])
df = df.sort_values("date")
df = df.set_index("date")

df["return"] = df["close"].pct_change()
df["equity"] = (1 + df["return"]).cumprod()

total_return = df["equity"].iloc[-1] - 1
num_days = len(df)
annualized_return = df["equity"].iloc[-1] ** (252 / num_days) - 1
annualized_volatility = df["return"].std() * np.sqrt(252)
sharpe_ratio = annualized_return / annualized_volatility

df["running_max"] = df["equity"].cummax()
df["drawdown"] = df["equity"] / df["running_max"] - 1
max_drawdown = df["drawdown"].min()

print(f"Total Return: {total_return:.2%}")
print(f"Annualized Return: {annualized_return:.2%}")
print(f"Annualized Volatility: {annualized_volatility:.2%}")
print(f"Sharpe Ratio: {sharpe_ratio:.2f}")
print(f"Max Drawdown: {max_drawdown:.2%}")

df["close"].plot(title="2330 Close Price")
plt.show()

df["equity"].plot(title="2330 Buy and Hold Equity Curve")
plt.show()

df["drawdown"].plot(title="2330 Drawdown")
plt.show()