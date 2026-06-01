import numpy as np
import pandas as pd


def equal_weight_portfolio(close_table):
    returns = close_table.pct_change().fillna(0)

    n = len(close_table.columns)
    weights = np.array([1 / n] * n)

    portfolio_return = returns.dot(weights)
    portfolio_equity = (1 + portfolio_return).cumprod()

    return pd.DataFrame({
        "portfolio_return": portfolio_return,
        "portfolio_equity": portfolio_equity,
    })


def monthly_rebalance_portfolio(close_table, initial_cash=100000):
    stock_ids = close_table.columns
    n = len(stock_ids)

    cash = initial_cash
    shares = {stock_id: 0 for stock_id in stock_ids}

    records = []
    current_month = None

    for date, prices in close_table.iterrows():
        if current_month != (date.year, date.month):
            current_month = (date.year, date.month)

            portfolio_value = cash

            for stock_id in stock_ids:
                portfolio_value += shares[stock_id] * prices[stock_id]

            target_value = portfolio_value / n
            cash = portfolio_value

            for stock_id in stock_ids:
                shares[stock_id] = target_value / prices[stock_id]

            cash = 0

        portfolio_value = cash

        for stock_id in stock_ids:
            portfolio_value += shares[stock_id] * prices[stock_id]

        record = {
            "date": date,
            "portfolio_value": portfolio_value,
        }

        for stock_id in stock_ids:
            record[f"{stock_id}_shares"] = shares[stock_id]

        records.append(record)

    result = pd.DataFrame(records)
    result = result.set_index("date")

    result["equity"] = result["portfolio_value"] / initial_cash
    result["return"] = result["portfolio_value"].pct_change().fillna(0)

    return result


def cross_sectional_momentum(
    close_table,
    lookback=60,
    top_n=2,
    rebalance_freq="ME",
):
    returns = close_table.pct_change().replace([np.inf, -np.inf], np.nan)

    momentum = close_table / close_table.shift(lookback) - 1

    weights = pd.DataFrame(
        np.nan,
        index=close_table.index,
        columns=close_table.columns,
    )

    rebalance_dates = close_table.resample(rebalance_freq).last().index

    for date in rebalance_dates:
        available_dates = momentum.index[momentum.index <= date]

        if len(available_dates) == 0:
            continue

        actual_date = available_dates[-1]
        scores = momentum.loc[actual_date].dropna()

        if len(scores) < top_n:
            continue

        selected = scores.sort_values(ascending=False).head(top_n).index

        weights.loc[actual_date] = 0.0
        weights.loc[actual_date, selected] = 1 / top_n

    weights = weights.ffill().fillna(0)
    weights = weights.shift(1).fillna(0)

    portfolio_return = (weights * returns).sum(axis=1).fillna(0)
    portfolio_equity = (1 + portfolio_return).cumprod()

    result = pd.DataFrame({
        "portfolio_return": portfolio_return,
        "portfolio_equity": portfolio_equity,
    })

    return result, weights
