import numpy as np

from config import (
    DEFAULT_PRICE_COL,
    DEFAULT_BUY_COST,
    DEFAULT_SELL_COST,
)


def buy_and_hold(df, price_col=DEFAULT_PRICE_COL):
    df = df.copy()

    df["return"] = df[price_col].pct_change()
    df["equity"] = (1 + df["return"].fillna(0)).cumprod()

    return df


def ma_strategy(
    df,
    short_window=20,
    long_window=60,
    price_col=DEFAULT_PRICE_COL,
    buy_cost=DEFAULT_BUY_COST,
    sell_cost=DEFAULT_SELL_COST,
):
    df = df.copy()

    df["return"] = df[price_col].pct_change()

    df["short_ma"] = df[price_col].rolling(short_window).mean()
    df["long_ma"] = df[price_col].rolling(long_window).mean()

    df["signal"] = 0
    df.loc[df["short_ma"] > df["long_ma"], "signal"] = 1

    # 用昨天訊號決定今天持倉，避免 look-ahead bias
    df["position"] = df["signal"].shift(1).fillna(0)

    df["position_change"] = df["position"].diff().fillna(0)
    df["buy_trade"] = (df["position_change"] > 0).astype(int)
    df["sell_trade"] = (df["position_change"] < 0).astype(int)
    df["trade"] = df["position_change"].abs()

    df["strategy_return"] = df["position"] * df["return"]

    df["strategy_return_with_cost"] = (
        df["strategy_return"]
        - df["buy_trade"] * buy_cost
        - df["sell_trade"] * sell_cost
    )

    df["buy_hold_equity"] = (1 + df["return"].fillna(0)).cumprod()
    df["strategy_equity"] = (1 + df["strategy_return"].fillna(0)).cumprod()
    df["strategy_equity_with_cost"] = (
        1 + df["strategy_return_with_cost"].fillna(0)
    ).cumprod()

    return df


def mean_reversion_strategy(
    df,
    window=20,
    entry_z=-2,
    exit_z=0,
    price_col=DEFAULT_PRICE_COL,
    buy_cost=DEFAULT_BUY_COST,
    sell_cost=DEFAULT_SELL_COST,
):
    df = df.copy()

    df["return"] = df[price_col].pct_change()

    df["ma"] = df[price_col].rolling(window).mean()
    df["std"] = df[price_col].rolling(window).std()
    df["zscore"] = (df[price_col] - df["ma"]) / df["std"]

    df["signal"] = np.nan

    df.loc[df["zscore"] < entry_z, "signal"] = 1
    df.loc[df["zscore"] > exit_z, "signal"] = 0

    df["signal"] = df["signal"].ffill().fillna(0)

    df["position"] = df["signal"].shift(1).fillna(0)

    df["position_change"] = df["position"].diff().fillna(0)
    df["buy_trade"] = (df["position_change"] > 0).astype(int)
    df["sell_trade"] = (df["position_change"] < 0).astype(int)
    df["trade"] = df["position_change"].abs()

    df["strategy_return"] = df["position"] * df["return"]

    df["strategy_return_with_cost"] = (
        df["strategy_return"]
        - df["buy_trade"] * buy_cost
        - df["sell_trade"] * sell_cost
    )

    df["buy_hold_equity"] = (1 + df["return"].fillna(0)).cumprod()
    df["strategy_equity_with_cost"] = (
        1 + df["strategy_return_with_cost"].fillna(0)
    ).cumprod()

    return df


def time_series_momentum_strategy(
    df,
    lookback=60,
    price_col=DEFAULT_PRICE_COL,
    buy_cost=DEFAULT_BUY_COST,
    sell_cost=DEFAULT_SELL_COST,
):
    df = df.copy()

    df["return"] = df[price_col].pct_change()
    df["momentum"] = df[price_col] / df[price_col].shift(lookback) - 1

    df["signal"] = 0
    df.loc[df["momentum"] > 0, "signal"] = 1

    df["position"] = df["signal"].shift(1).fillna(0)

    df["position_change"] = df["position"].diff().fillna(0)
    df["buy_trade"] = (df["position_change"] > 0).astype(int)
    df["sell_trade"] = (df["position_change"] < 0).astype(int)
    df["trade"] = df["position_change"].abs()

    df["strategy_return"] = df["position"] * df["return"]

    df["strategy_return_with_cost"] = (
        df["strategy_return"]
        - df["buy_trade"] * buy_cost
        - df["sell_trade"] * sell_cost
    )

    df["buy_hold_equity"] = (1 + df["return"].fillna(0)).cumprod()
    df["strategy_equity_with_cost"] = (
        1 + df["strategy_return_with_cost"].fillna(0)
    ).cumprod()

    return df