import pandas as pd
import matplotlib.pyplot as plt


def plot_price_with_ma(df, title="Price with Moving Averages"):
    df[["close", "short_ma", "long_ma"]].plot(
        title=title,
        figsize=(12, 6),
    )
    plt.show()


def plot_equity(equity_dict, title="Equity Curve"):
    plot_df = pd.DataFrame(equity_dict)

    plot_df.plot(
        title=title,
        figsize=(12, 6),
    )

    plt.show()


def plot_rolling_sharpe(series, title="Rolling Sharpe"):
    series.plot(
        title=title,
        figsize=(12, 6),
    )

    plt.axhline(0)
    plt.show()