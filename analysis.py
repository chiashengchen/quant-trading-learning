import numpy as np
import pandas as pd

from config import TRADING_DAYS
from metrics import performance_metrics_from_returns


def rolling_sharpe(returns, window=252):
    rolling_mean = returns.rolling(window).mean() * TRADING_DAYS
    rolling_vol = returns.rolling(window).std() * np.sqrt(TRADING_DAYS)

    return rolling_mean / rolling_vol


def build_strategy_comparison(strategy_returns_dict):
    results = []

    for name, returns in strategy_returns_dict.items():
        metrics = performance_metrics_from_returns(returns)
        metrics["strategy"] = name
        results.append(metrics)

    table = pd.DataFrame(results)

    return table[
        [
            "strategy",
            "total_return",
            "annualized_return",
            "annualized_volatility",
            "sharpe_ratio",
            "max_drawdown",
        ]
    ]


def exposure_time(position):
    return position.mean()


def trade_summary(trades):
    if trades.empty:
        return {
            "num_trades": 0,
            "win_rate": None,
            "average_trade_return": None,
            "best_trade": None,
            "worst_trade": None,
        }

    return {
        "num_trades": len(trades),
        "win_rate": (trades["trade_return"] > 0).mean(),
        "average_trade_return": trades["trade_return"].mean(),
        "best_trade": trades["trade_return"].max(),
        "worst_trade": trades["trade_return"].min(),
    }