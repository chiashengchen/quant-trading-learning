from data_loader import (
    load_stock_data,
    load_multiple_stocks,
    build_clean_close_table,
)

from data_validation import validate_price_table

from strategies import (
    buy_and_hold,
    ma_strategy,
    mean_reversion_strategy,
    time_series_momentum_strategy,
)

from backtest import (
    compare_ma_params,
    train_test_ma,
    walk_forward_test,
    add_ma_signal,
    cash_backtest,
    extract_trades,
)

from portfolio import (
    equal_weight_portfolio,
    monthly_rebalance_portfolio,
    cross_sectional_momentum,
)

from metrics import (
    performance_metrics_from_returns,
    performance_metrics_from_equity,
    print_metrics,
    format_result_table,
)

from analysis import (
    rolling_sharpe,
    build_strategy_comparison,
    trade_summary,
)

from plotting import (
    plot_price_with_ma,
    plot_equity,
    plot_rolling_sharpe,
)


def main():
    stock_id = "0050"
    start_date = "2015-01-01"
    end_date = "2025-01-01"

    # 之後如果你有 adjusted close，可以把 price_col 改成 "adj_close"
    price_col = "close"

    df = load_stock_data(stock_id, start_date, end_date)

    validate_price_table(df[[price_col]])

    # Week 1: Buy and Hold
    bh_df = buy_and_hold(df, price_col=price_col)
    bh_metrics = performance_metrics_from_returns(bh_df["return"])
    print_metrics("Buy and Hold", bh_metrics)

    # Week 2-3: MA Strategy
    ma_df = ma_strategy(
        df,
        short_window=20,
        long_window=60,
        price_col=price_col,
    )

    ma_metrics = performance_metrics_from_returns(
        ma_df["strategy_return_with_cost"]
    )

    print_metrics("MA20/60 Strategy", ma_metrics)

    # Week 7: Mean Reversion
    mr_df = mean_reversion_strategy(
        df,
        window=20,
        entry_z=-2,
        exit_z=0,
        price_col=price_col,
    )

    mr_metrics = performance_metrics_from_returns(
        mr_df["strategy_return_with_cost"]
    )

    print_metrics("Mean Reversion Strategy", mr_metrics)

    # Week 8: Time-Series Momentum
    mom_df = time_series_momentum_strategy(
        df,
        lookback=60,
        price_col=price_col,
    )

    mom_metrics = performance_metrics_from_returns(
        mom_df["strategy_return_with_cost"]
    )

    print_metrics("Time-Series Momentum Strategy", mom_metrics)

    # Week 3: MA Parameter Comparison
    param_list = [
        (5, 20),
        (20, 60),
        (50, 200),
    ]

    ma_param_table = compare_ma_params(
        df,
        param_list,
        price_col=price_col,
    )

    print("\nMA Parameter Comparison")
    print(format_result_table(ma_param_table))

    # Week 3: Train / Test
    tt_result = train_test_ma(
        df=df,
        param_list=param_list,
        train_start="2015-01-01",
        train_end="2020-12-31",
        test_start="2021-01-01",
        test_end="2025-01-01",
        price_col=price_col,
    )

    print("\nTrain Result")
    print(format_result_table(tt_result["train_result"]))

    print("\nBest MA Parameters")
    print("Short MA:", tt_result["best_short"])
    print("Long MA:", tt_result["best_long"])

    print_metrics("Test Performance", tt_result["test_metrics"])

    # Week 6: Walk Forward
    wf_result = walk_forward_test(
        df=df,
        param_list=param_list,
        train_years=3,
        test_years=1,
        price_col=price_col,
    )

    print("\nWalk Forward Result")
    print(format_result_table(wf_result))

    # Week 4: Cash Backtest
    df_signal = add_ma_signal(
        df,
        short_window=20,
        long_window=60,
        price_col=price_col,
    )

    cash_result = cash_backtest(
        df_signal,
        initial_cash=100000,
        fee_rate=0.001425,
        tax_rate=0.003,
        execution_price_col="close",
    )

    cash_metrics = performance_metrics_from_equity(cash_result["equity"])
    print_metrics("Cash Backtest MA20/60", cash_metrics)

    trades = extract_trades(cash_result)

    print("\nTrade Records")
    print(trades)

    print("\nTrade Summary")
    print(trade_summary(trades))

    # Week 6: Rolling Sharpe
    ma_df["rolling_sharpe"] = rolling_sharpe(
        ma_df["strategy_return_with_cost"],
        window=252,
    )

    # Week 5 / 8: Portfolio
    stock_ids = ["0050", "2330", "2317", "2454", "2303"]

    data = load_multiple_stocks(
        stock_ids,
        start_date=start_date,
        end_date=end_date,
    )

    close_table = build_clean_close_table(data, price_col="close")

    validate_price_table(close_table)

    eq_portfolio = equal_weight_portfolio(close_table)
    eq_metrics = performance_metrics_from_equity(
        eq_portfolio["portfolio_equity"]
    )
    print_metrics("Equal Weight Portfolio", eq_metrics)

    monthly_result = monthly_rebalance_portfolio(close_table)
    monthly_metrics = performance_metrics_from_equity(
        monthly_result["equity"]
    )
    print_metrics("Monthly Rebalance Portfolio", monthly_metrics)

    cs_result, weights = cross_sectional_momentum(
        close_table,
        lookback=60,
        top_n=2,
        rebalance_freq="ME",
    )

    cs_metrics = performance_metrics_from_equity(
        cs_result["portfolio_equity"]
    )
    print_metrics("Cross-Sectional Momentum", cs_metrics)

    # Strategy comparison
    strategy_returns = {
        "Buy and Hold": bh_df["return"],
        "MA20/60": ma_df["strategy_return_with_cost"],
        "Mean Reversion": mr_df["strategy_return_with_cost"],
        "Time-Series Momentum": mom_df["strategy_return_with_cost"],
        "Equal Weight Portfolio": eq_portfolio["portfolio_return"],
        "Cross-Sectional Momentum": cs_result["portfolio_return"],
    }

    comparison_table = build_strategy_comparison(strategy_returns)

    print("\nStrategy Comparison")
    print(format_result_table(comparison_table))

    # Plots
    plot_price_with_ma(ma_df, title="0050 Price with MA20/60")

    plot_equity(
        {
            "Buy and Hold": bh_df["equity"],
            "MA20/60": ma_df["strategy_equity_with_cost"],
            "Mean Reversion": mr_df["strategy_equity_with_cost"],
            "Momentum": mom_df["strategy_equity_with_cost"],
        },
        title="Single Asset Strategy Comparison",
    )

    plot_rolling_sharpe(
        ma_df["rolling_sharpe"],
        title="MA20/60 Rolling 1-Year Sharpe",
    )

    plot_equity(
        {
            "Equal Weight": eq_portfolio["portfolio_equity"],
            "Monthly Rebalance": monthly_result["equity"],
            "Cross-Sectional Momentum": cs_result["portfolio_equity"],
        },
        title="Portfolio Strategy Comparison",
    )


if __name__ == "__main__":
    main()