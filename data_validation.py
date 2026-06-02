import numpy as np


def validate_price_table(price_table):
    print("Shape:", price_table.shape)

    print("\nNaN count:")
    print(price_table.isna().sum())

    print("\nZero count:")
    print((price_table == 0).sum())

    print("\nNegative price count:")
    print((price_table < 0).sum())

    returns = price_table.pct_change()

    print("\nInf return count:")
    print(np.isinf(returns).sum())

    bad_rows = returns[np.isinf(returns).any(axis=1)]

    if not bad_rows.empty:
        print("\nRows with inf returns:")
        print(bad_rows)

    extreme_returns = returns[(returns.abs() > 0.3).any(axis=1)]

    if not extreme_returns.empty:
        print("\nRows with extreme returns > 30%:")
        print(extreme_returns)