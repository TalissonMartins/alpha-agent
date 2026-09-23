import pandas as pd

from src.data import data_fetcher


def test_to_percent_uses_yfinance_decimal_contract():
    assert data_fetcher._to_percent(0.06) == 6.0
    assert data_fetcher._to_percent(0) == 0.0
    assert data_fetcher._to_percent(None) is None


def test_fetch_multiple_tickers_exposes_partial_failures(monkeypatch):
    class FakeTicker:
        def __init__(self, symbol):
            if symbol == "BAD.SA":
                raise RuntimeError("ticker unavailable")
            self.info = {
                "shortName": "Good",
                "sector": "Technology",
                "currentPrice": 10.0,
                "trailingPE": 10.0,
                "priceToBook": 2.0,
                "dividendYield": 0.06,
            }

    monkeypatch.setattr(data_fetcher.yf, "Ticker", FakeTicker)
    monkeypatch.setattr(data_fetcher.time, "sleep", lambda _: None)

    result = data_fetcher.fetch_multiple_tickers(["GOOD.SA", "BAD.SA"])

    assert isinstance(result, pd.DataFrame)
    assert result.loc[result["Ticker"] == "GOOD", "Status_Coleta"].iloc[0] == "ok"
    failed = result.loc[result["Ticker"] == "BAD"].iloc[0]
    assert failed["Status_Coleta"] == "erro"
    assert failed["Erro_Coleta"] == "ticker unavailable"
