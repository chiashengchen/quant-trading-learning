"""
Tests for database.py — save, load, and latest-date queries.
All DB calls go to an in-memory SQLite via the patch_db fixture.
"""
import pandas as pd
import pytest

from database import save_daily_prices, load_daily_prices_from_db, get_latest_price_date


class TestSaveDailyPrices:
    def test_saves_rows(self, patch_db, sample_price_df):
        save_daily_prices("0050", sample_price_df)

        cursor = patch_db.execute("SELECT COUNT(*) FROM daily_prices WHERE stock_id = '0050'")
        assert cursor.fetchone()[0] == 5

    def test_upsert_does_not_duplicate(self, patch_db, sample_price_df):
        save_daily_prices("0050", sample_price_df)
        save_daily_prices("0050", sample_price_df)

        cursor = patch_db.execute("SELECT COUNT(*) FROM daily_prices WHERE stock_id = '0050'")
        assert cursor.fetchone()[0] == 5

    def test_close_value_preserved(self, patch_db, sample_price_df):
        save_daily_prices("0050", sample_price_df)

        df = load_daily_prices_from_db("0050")
        assert df["close"].iloc[0] == pytest.approx(100.5)


class TestLoadDailyPricesFromDb:
    def test_returns_empty_df_when_no_data(self, patch_db):
        df = load_daily_prices_from_db("9999")
        assert df.empty

    def test_date_filter_start(self, patch_db, sample_price_df):
        save_daily_prices("0050", sample_price_df)

        df = load_daily_prices_from_db("0050", start_date="2024-01-04")
        assert df.index.min() >= pd.Timestamp("2024-01-04")

    def test_date_filter_end(self, patch_db, sample_price_df):
        save_daily_prices("0050", sample_price_df)

        df = load_daily_prices_from_db("0050", end_date="2024-01-03")
        assert df.index.max() <= pd.Timestamp("2024-01-03")

    def test_index_is_datetime(self, patch_db, sample_price_df):
        save_daily_prices("0050", sample_price_df)

        df = load_daily_prices_from_db("0050")
        assert pd.api.types.is_datetime64_any_dtype(df.index)

    def test_sorted_ascending(self, patch_db, sample_price_df):
        save_daily_prices("0050", sample_price_df)

        df = load_daily_prices_from_db("0050")
        assert list(df.index) == sorted(df.index)


class TestGetLatestPriceDate:
    def test_returns_none_when_empty(self, patch_db):
        result = get_latest_price_date("9999")
        assert result is None

    def test_returns_max_date(self, patch_db, sample_price_df):
        save_daily_prices("0050", sample_price_df)

        latest = get_latest_price_date("0050")
        assert latest == "2024-01-08"
