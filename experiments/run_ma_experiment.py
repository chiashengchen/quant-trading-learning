import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from config import TABLE_DIR, FIGURE_DIR
from data_loader import load_stock_data
from data_validation import validate_price_table
from strategies import buy_and_hold, ma_strategy
from metrics import performance_metrics_from_returns, print_metrics
from plotting import plot_equity


CONFIG = {
    "stock_id": "0050",
    "start_date": "2015-01-01",
    "end_date": "2025-01-01",
    "strategy": "ma_crossover",
    "price_col": "close",
    "params": {
        "short_window": 20,
        "long_window": 60,
        "buy_cost": 0.001,
        "sell_cost": 0.0015,
    },
    "data": {
        "source": "FinMind",
        "price_type": "raw_close",
        "adjusted_for_dividend": False,
    },
}


def main():
    stock_id = CONFIG["stock_id"]
    start_date = CONFIG["start_date"]
    end_date = CONFIG["end_date"]
    price_col = CONFIG["price_col"]

    df = load_stock_data(stock_id, start_date, end_date)

    validate_price_table(df[[price_col]])

    bh_df = buy_and_hold(df, price_col=price_col)

    ma_df = ma_strategy(
        df,
        short_window=CONFIG["params"]["short_window"],
        long_window=CONFIG["params"]["long_window"],
        price_col=price_col,
        buy_cost=CONFIG["params"]["buy_cost"],
        sell_cost=CONFIG["params"]["sell_cost"],
    )

    bh_metrics = performance_metrics_from_returns(bh_df["return"])
    ma_metrics = performance_metrics_from_returns(
        ma_df["strategy_return_with_cost"]
    )

    print_metrics("Buy and Hold", bh_metrics)
    print_metrics("MA Strategy", ma_metrics)

    metrics_table = pd.DataFrame([
        {
            "strategy": "buy_and_hold",
            **bh_metrics,
        },
        {
            "strategy": "ma_crossover",
            **ma_metrics,
        },
    ])

    metrics_path = TABLE_DIR / f"ma_{stock_id}_metrics.csv"
    metrics_table.to_csv(metrics_path, index=False)

    equity_table = pd.DataFrame({
        "buy_and_hold": bh_df["equity"],
        "ma_strategy": ma_df["strategy_equity_with_cost"],
    })

    equity_path = TABLE_DIR / f"ma_{stock_id}_equity.csv"
    equity_table.to_csv(equity_path)

    figure_path = FIGURE_DIR / f"ma_{stock_id}_equity.png"

    plot_equity(
        {
            "Buy and Hold": bh_df["equity"],
            "MA20/60": ma_df["strategy_equity_with_cost"],
        },
        title=f"{stock_id} MA20/60 vs Buy and Hold",
        save_path=figure_path,
    )

    print("\nSaved files:")
    print(metrics_path)
    print(equity_path)
    print(figure_path)



if __name__ == "__main__":
    main()