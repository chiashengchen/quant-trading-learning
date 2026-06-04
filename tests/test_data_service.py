"""
Tests for data_service.py — cache-first logic and incremental update logic.
API calls (load_stock_data) are mocked; DB calls use in-memory SQLite.
"""
import pandas as pd
import pytest

import data_service
from repositories import save_daily_prices, load_daily_prices


class TestGetDailyPrices:
    def test_returns_from_cache_without_api_call(self, patch_db, sample_price_df, monkeypatch):
        save_daily_prices("0050", sample_price_df)

        fetch_called = []
        monkeypatch.setattr(
            data_service, "fetch_and_store_stock_data",
            lambda *a, **kw: fetch_called.append(a),
        )

        df = data_service.get_daily_prices("0050", "2024-01-02", "2024-01-08")
        assert not df.empty
        assert fetch_called == [], "API should not be called when cache has data"

    def test_fetches_when_cache_empty(self, patch_db, sample_price_df, monkeypatch):
        monkeypatch.setattr(
            data_service, "fetch_and_store_stock_data",
            lambda stock_id, start, end: save_daily_prices(stock_id, sample_price_df),
        )
        monkeypatch.setattr(data_service, "init_db", lambda: None)

        df = data_service.get_daily_prices("0050", "2024-01-02", "2024-01-08")
        assert not df.empty

    def test_auto_fetch_false_returns_empty_when_no_cache(self, patch_db, monkeypatch):
        monkeypatch.setattr(data_service, "init_db", lambda: None)

        df = data_service.get_daily_prices("0050", "2024-01-02", "2024-01-08", auto_fetch=False)
        assert df.empty


class TestUpdateDailyPrices:
    def test_skips_fetch_when_up_to_date(self, patch_db, sample_price_df, monkeypatch):
        save_daily_prices("0050", sample_price_df)  # latest date = 2024-01-08

        fetch_called = []
        monkeypatch.setattr(
            data_service, "fetch_and_store_stock_data",
            lambda *a, **kw: fetch_called.append(a),
        )
        monkeypatch.setattr(data_service, "init_db", lambda: None)

        data_service.update_daily_prices("0050", "2024-01-02", "2024-01-07")
        assert fetch_called == [], "should not re-fetch when end_date is before latest stored date"

    def test_fetches_only_missing_range(self, patch_db, sample_price_df, monkeypatch):
        save_daily_prices("0050", sample_price_df)  # up to 2024-01-08

        captured = {}
        def fake_fetch(stock_id, start, end):
            captured["start"] = start
            captured["end"] = end

        monkeypatch.setattr(data_service, "fetch_and_store_stock_data", fake_fetch)
        monkeypatch.setattr(data_service, "init_db", lambda: None)

        data_service.update_daily_prices("0050", "2024-01-02", "2024-01-15")
        assert captured["start"] == "2024-01-09"  # day after latest stored
        assert captured["end"] == "2024-01-15"
