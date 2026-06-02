import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def plot_price_with_ma(df, title="Price with Moving Averages", save_path=None):
    ax = df[["close", "short_ma", "long_ma"]].plot(
        title=title,
        figsize=(12, 6),
    )

    fig = ax.get_figure()

    if save_path is not None:
        fig.savefig(save_path, bbox_inches="tight")

    plt.show()


def plot_equity(equity_dict, title="Equity Curve", save_path=None):
    plot_df = pd.DataFrame(equity_dict)

    plot_df = plot_df.replace([np.inf, -np.inf], np.nan)
    plot_df = plot_df.dropna(how="all")

    print("\nPlot data check:")
    print(plot_df.head())
    print(plot_df.tail())
    print(plot_df.isna().sum())
    print(plot_df.shape)

    ax = plot_df.plot(
        title=title,
        figsize=(12, 6),
    )

    fig = ax.get_figure()

    if save_path is not None:
        fig.savefig(save_path, bbox_inches="tight")

    plt.show()


def plot_rolling_sharpe(series, title="Rolling Sharpe", save_path=None):
    ax = series.plot(
        title=title,
        figsize=(12, 6),
    )

    plt.axhline(0)

    fig = ax.get_figure()

    if save_path is not None:
        fig.savefig(save_path, bbox_inches="tight")

    plt.show()