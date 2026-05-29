from FinMind.data import DataLoader
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


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


def ma_strategy(df, short_window, long_window, cost=0.001):
    df = df.copy()

    df["return"] = df["close"].pct_change()

    df["short_ma"] = df["close"].rolling(short_window).mean()
    df["long_ma"] = df["close"].rolling(long_window).mean()

    df["signal"] = 0
    df.loc[df["short_ma"] > df["long_ma"], "signal"] = 1

    df["position"] = df["signal"].shift(1).fillna(0)

    df["trade"] = df["position"].diff().abs().fillna(0)

    df["strategy_return"] = df["position"] * df["return"]

    df["strategy_return_with_cost"] = df["strategy_return"] - df["trade"] * cost

    df["buy_hold_equity"] = (1 + df["return"].fillna(0)).cumprod()
    df["strategy_equity"] = (1 + df["strategy_return"].fillna(0)).cumprod()
    df["strategy_equity_with_cost"] = (
        1 + df["strategy_return_with_cost"].fillna(0)
    ).cumprod()

    return df


def performance_metrics(df, return_col):
    returns = df[return_col].fillna(0)

    equity = (1 + returns).cumprod()

    total_return = equity.iloc[-1] - 1
    annualized_return = equity.iloc[-1] ** (252 / len(equity)) - 1
    annualized_volatility = returns.std() * np.sqrt(252)

    if annualized_volatility == 0:
        sharpe_ratio = np.nan
    else:
        sharpe_ratio = annualized_return / annualized_volatility

    running_max = equity.cummax()
    drawdown = equity / running_max - 1
    max_drawdown = drawdown.min()

    return {
        "total_return": total_return,
        "annualized_return": annualized_return,
        "annualized_volatility": annualized_volatility,
        "sharpe_ratio": sharpe_ratio,
        "max_drawdown": max_drawdown
    }


def compare_ma_params(df, param_list, cost=0.001):
    results = []

    for short_window, long_window in param_list:
        result_df = ma_strategy(
            df=df,
            short_window=short_window,
            long_window=long_window,
            cost=cost
        )

        metrics = performance_metrics(
            result_df,
            return_col="strategy_return_with_cost"
        )

        metrics["short_window"] = short_window
        metrics["long_window"] = long_window
        metrics["num_trades"] = int(result_df["trade"].sum())

        results.append(metrics)

    result_table = pd.DataFrame(results)

    result_table = result_table[
        [
            "short_window",
            "long_window",
            "total_return",
            "annualized_return",
            "annualized_volatility",
            "sharpe_ratio",
            "max_drawdown",
            "num_trades"
        ]
    ]

    return result_table


def format_result_table(result_table):
    display_table = result_table.copy()

    percent_cols = [
        "total_return",
        "annualized_return",
        "annualized_volatility",
        "max_drawdown"
    ]

    for col in percent_cols:
        display_table[col] = display_table[col].map(lambda x: f"{x:.2%}")

    display_table["sharpe_ratio"] = display_table["sharpe_ratio"].map(
        lambda x: f"{x:.2f}"
    )

    return display_table


# =========================
# Main
# =========================

df = load_stock_data(
    stock_id="0050",
    start_date="2015-01-01",
    end_date="2025-01-01"
)

param_list = [
    (5, 20),
    (20, 60),
    (50, 200),
]

# Full period comparison
result_table = compare_ma_params(
    df=df,
    param_list=param_list,
    cost=0.001
)

print("Full Period Result")
print(format_result_table(result_table))


# Buy and Hold
df_buy_hold = df.copy()
df_buy_hold["return"] = df_buy_hold["close"].pct_change() # curr / prev - 1

buy_hold_metrics = performance_metrics(df_buy_hold, "return")

print("\nBuy and Hold Performance")
print(f"Total Return: {buy_hold_metrics['total_return']:.2%}")
print(f"Annualized Return: {buy_hold_metrics['annualized_return']:.2%}")
print(f"Annualized Volatility: {buy_hold_metrics['annualized_volatility']:.2%}")
print(f"Sharpe Ratio: {buy_hold_metrics['sharpe_ratio']:.2f}")
print(f"Max Drawdown: {buy_hold_metrics['max_drawdown']:.2%}")


# Plot MA20/MA60
df_20_60 = ma_strategy(
    df=df,
    short_window=20,
    long_window=60,
    cost=0.001
)

df_20_60[["close", "short_ma", "long_ma"]].plot(
    title="0050 Price with MA20 / MA60",
    figsize=(12, 6)
)
plt.show()

df_20_60[
    ["buy_hold_equity", "strategy_equity", "strategy_equity_with_cost"]
].plot(
    title="Buy & Hold vs MA Strategy",
    figsize=(12, 6)
)
plt.show()


# Train / Test Split
train_df = df.loc["2015-01-01":"2020-12-31"].copy()
test_df = df.loc["2021-01-01":"2025-01-01"].copy()

train_result_table = compare_ma_params(
    df=train_df,
    param_list=param_list,
    cost=0.001
)

print("\nTrain Result")
print(format_result_table(train_result_table))

best_row = train_result_table.sort_values(
    "sharpe_ratio",
    ascending=False
).iloc[0]

best_short = int(best_row["short_window"])
best_long = int(best_row["long_window"])

print("\nBest Parameters from Train Period")
print("Short MA:", best_short)
print("Long MA:", best_long)
print(f"Train Sharpe: {best_row['sharpe_ratio']:.2f}")

test_result_df = ma_strategy(
    df=test_df,
    short_window=best_short,
    long_window=best_long,
    cost=0.001
)

test_metrics = performance_metrics(
    test_result_df,
    return_col="strategy_return_with_cost"
)

print("\nTest Performance")
print(f"Total Return: {test_metrics['total_return']:.2%}")
print(f"Annualized Return: {test_metrics['annualized_return']:.2%}")
print(f"Annualized Volatility: {test_metrics['annualized_volatility']:.2%}")
print(f"Sharpe Ratio: {test_metrics['sharpe_ratio']:.2f}")
print(f"Max Drawdown: {test_metrics['max_drawdown']:.2%}")

test_result_df[
    ["buy_hold_equity", "strategy_equity_with_cost"]
].plot(
    title=f"Test Period: Buy & Hold vs MA{best_short}/{best_long} Strategy",
    figsize=(12, 6)
)
plt.show()