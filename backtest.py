import pandas as pd

from config import (
    DEFAULT_PRICE_COL,
    DEFAULT_INITIAL_CASH,
    DEFAULT_FEE_RATE,
    DEFAULT_TAX_RATE,
)

from metrics import performance_metrics_from_returns
from strategies import ma_strategy


def compare_ma_params(df, param_list, price_col=DEFAULT_PRICE_COL):
    results = []

    for short_window, long_window in param_list:
        result_df = ma_strategy(
            df=df,
            short_window=short_window,
            long_window=long_window,
            price_col=price_col,
        )

        metrics = performance_metrics_from_returns(
            result_df["strategy_return_with_cost"]
        )

        metrics["short_window"] = short_window
        metrics["long_window"] = long_window
        metrics["num_trades"] = int(result_df["trade"].sum())

        results.append(metrics)

    result_table = pd.DataFrame(results)

    return result_table[
        [
            "short_window",
            "long_window",
            "total_return",
            "annualized_return",
            "annualized_volatility",
            "sharpe_ratio",
            "max_drawdown",
            "num_trades",
        ]
    ]


def train_test_ma(
    df,
    param_list,
    train_start,
    train_end,
    test_start,
    test_end,
    price_col=DEFAULT_PRICE_COL,
):
    train_df = df.loc[train_start:train_end].copy()
    test_df = df.loc[test_start:test_end].copy()

    train_result = compare_ma_params(train_df, param_list, price_col=price_col)

    best_row = train_result.sort_values(
        "sharpe_ratio",
        ascending=False,
    ).iloc[0]

    best_short = int(best_row["short_window"])
    best_long = int(best_row["long_window"])

    test_result_df = ma_strategy(
        test_df,
        short_window=best_short,
        long_window=best_long,
        price_col=price_col,
    )

    test_metrics = performance_metrics_from_returns(
        test_result_df["strategy_return_with_cost"]
    )

    return {
        "train_result": train_result,
        "best_short": best_short,
        "best_long": best_long,
        "test_result_df": test_result_df,
        "test_metrics": test_metrics,
    }


def walk_forward_test(
    df,
    param_list,
    train_years=3,
    test_years=1,
    price_col=DEFAULT_PRICE_COL,
):
    results = []

    start_year = df.index.min().year
    end_year = df.index.max().year

    for train_start in range(start_year, end_year - train_years - test_years + 2):
        train_end = train_start + train_years - 1
        test_start = train_end + 1
        test_end = test_start + test_years - 1

        train_df = df.loc[f"{train_start}-01-01":f"{train_end}-12-31"].copy()
        test_df = df.loc[f"{test_start}-01-01":f"{test_end}-12-31"].copy()

        if len(train_df) == 0 or len(test_df) == 0:
            continue

        train_table = compare_ma_params(
            train_df,
            param_list,
            price_col=price_col,
        )

        best = train_table.sort_values(
            "sharpe_ratio",
            ascending=False,
        ).iloc[0]

        best_short = int(best["short_window"])
        best_long = int(best["long_window"])

        test_result = ma_strategy(
            test_df,
            best_short,
            best_long,
            price_col=price_col,
        )

        test_metrics = performance_metrics_from_returns(
            test_result["strategy_return_with_cost"]
        )

        results.append({
            "train_start": train_start,
            "train_end": train_end,
            "test_start": test_start,
            "test_end": test_end,
            "best_short": best_short,
            "best_long": best_long,
            "test_total_return": test_metrics["total_return"],
            "test_sharpe": test_metrics["sharpe_ratio"],
            "test_max_drawdown": test_metrics["max_drawdown"],
        })

    return pd.DataFrame(results)


def add_ma_signal(df, short_window=20, long_window=60, price_col=DEFAULT_PRICE_COL):
    df = df.copy()

    df["short_ma"] = df[price_col].rolling(short_window).mean()
    df["long_ma"] = df[price_col].rolling(long_window).mean()

    df["signal"] = 0
    df.loc[df["short_ma"] > df["long_ma"], "signal"] = 1

    df["position_signal"] = df["signal"].shift(1).fillna(0)

    return df


def cash_backtest(
    df,
    initial_cash=DEFAULT_INITIAL_CASH,
    fee_rate=DEFAULT_FEE_RATE,
    tax_rate=DEFAULT_TAX_RATE,
    execution_price_col="close",
):
    """
    真實成交模擬：
    - signal 可以由 adjusted close 產生
    - 但 execution 應該用 raw close / open
    """
    df = df.copy()

    cash = initial_cash
    shares = 0
    prev_position = 0

    records = []

    for date, row in df.iterrows():
        price = row[execution_price_col]
        target_position = row["position_signal"]

        action = "HOLD"
        fee = 0
        tax = 0

        if prev_position == 0 and target_position == 1:
            fee = cash * fee_rate
            buy_amount = cash - fee

            shares = buy_amount / price
            cash = 0
            action = "BUY"

        elif prev_position == 1 and target_position == 0:
            sell_amount = shares * price
            fee = sell_amount * fee_rate
            tax = sell_amount * tax_rate

            cash = sell_amount - fee - tax
            shares = 0
            action = "SELL"

        portfolio_value = cash + shares * price

        records.append({
            "date": date,
            "price": price,
            "signal": row["signal"],
            "position_signal": target_position,
            "action": action,
            "cash": cash,
            "shares": shares,
            "fee": fee,
            "tax": tax,
            "portfolio_value": portfolio_value,
        })

        prev_position = target_position

    result = pd.DataFrame(records)
    result = result.set_index("date")

    result["return"] = result["portfolio_value"].pct_change().fillna(0)
    result["equity"] = result["portfolio_value"] / initial_cash

    return result


def extract_trades(result):
    trades = []

    in_trade = False
    entry_date = None
    entry_value = None

    for date, row in result.iterrows():
        action = row["action"]

        if action == "BUY" and not in_trade:
            in_trade = True
            entry_date = date
            entry_value = row["portfolio_value"]

        elif action == "SELL" and in_trade:
            exit_date = date
            exit_value = row["portfolio_value"]

            trade_return = exit_value / entry_value - 1

            trades.append({
                "entry_date": entry_date,
                "exit_date": exit_date,
                "entry_value": entry_value,
                "exit_value": exit_value,
                "trade_return": trade_return,
                "holding_days": (exit_date - entry_date).days,
            })

            in_trade = False

    return pd.DataFrame(trades)