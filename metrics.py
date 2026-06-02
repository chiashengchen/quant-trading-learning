import numpy as np
from config import TRADING_DAYS


def performance_metrics_from_returns(returns):
    returns = returns.fillna(0)
    equity = (1 + returns).cumprod()

    total_return = equity.iloc[-1] - 1
    annualized_return = equity.iloc[-1] ** (TRADING_DAYS / len(equity)) - 1
    annualized_volatility = returns.std() * np.sqrt(TRADING_DAYS)

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
        "max_drawdown": max_drawdown,
    }


def performance_metrics_from_equity(equity):
    equity = equity.dropna()
    returns = equity.pct_change().fillna(0)

    total_return = equity.iloc[-1] - 1
    annualized_return = equity.iloc[-1] ** (TRADING_DAYS / len(equity)) - 1
    annualized_volatility = returns.std() * np.sqrt(TRADING_DAYS)

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
        "max_drawdown": max_drawdown,
    }


def print_metrics(name, metrics):
    print(f"\n{name}")
    print(f"Total Return: {metrics['total_return']:.2%}")
    print(f"Annualized Return: {metrics['annualized_return']:.2%}")
    print(f"Annualized Volatility: {metrics['annualized_volatility']:.2%}")
    print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
    print(f"Max Drawdown: {metrics['max_drawdown']:.2%}")


def format_result_table(result_table):
    display_table = result_table.copy()

    percent_cols = [
        "total_return",
        "annualized_return",
        "annualized_volatility",
        "max_drawdown",
        "test_total_return",
        "test_max_drawdown",
    ]

    for col in percent_cols:
        if col in display_table.columns:
            display_table[col] = display_table[col].map(lambda x: f"{x:.2%}")

    for col in ["sharpe_ratio", "test_sharpe"]:
        if col in display_table.columns:
            display_table[col] = display_table[col].map(lambda x: f"{x:.2f}")

    return display_table