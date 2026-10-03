import pandas as pd

from src.portfolio.exterior import adicionar_preco_brl, tickers_usd


def test_le_somente_tickers_usd():
    carteira = {
        "posicoes": [
            {"classe": "RV_BR", "ticker": "PETR4"},
            {"classe": "RV_USD", "ticker": "aapl"},
            {"classe": "RF_BR", "nome": "Tesouro"},
        ]
    }
    assert tickers_usd(carteira) == ["AAPL"]


def test_converte_preco_para_brl():
    df = pd.DataFrame([{"Ticker": "AAPL", "Preco_Atual": 100.0}])
    out = adicionar_preco_brl(df, 5.4)
    assert out.loc[0, "Preco_BRL"] == 540.0
