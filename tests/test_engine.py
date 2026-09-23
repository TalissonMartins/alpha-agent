import pandas as pd
import pytest

from src.finance.engine import calculate_valuation


def test_calculate_valuation_adds_expected_indicators():
    data = pd.DataFrame(
        [{
            "Preco_Atual": 20.0,
            "PL": 10.0,
            "PVP": 2.0,
            "Dividend_Yield_%": 6.0,
            "Fluxo_Caixa_Livre": 100.0,
            "Acoes_Em_Circulacao": 10.0,
        }]
    )

    result = calculate_valuation(data)

    assert result.loc[0, "Preco_Justo_Graham"] == 21.21
    assert result.loc[0, "Earnings_Yield_%"] == 10.0
    assert result.loc[0, "Preco_Justo_Gordon"] == 15.6
    assert result.loc[0, "Margem_Graham_%"] == 5.7
    assert result.loc[0, "Preco_Justo_DCF"] == 130.0
    assert result.loc[0, "Margem_DCF_%"] == 84.62


def test_calculate_valuation_rejects_missing_required_columns():
    data = pd.DataFrame([{"Preco_Atual": 20.0, "PL": 10.0}])

    with pytest.raises(ValueError, match="PVP"):
        calculate_valuation(data)


def test_calculate_valuation_preserves_input():
    data = pd.DataFrame(
        [{
            "Preco_Atual": 20.0,
            "PL": 10.0,
            "PVP": 2.0,
            "Dividend_Yield_%": 6.0,
        }]
    )
    original_columns = list(data.columns)

    calculate_valuation(data)

    assert list(data.columns) == original_columns


def test_calculate_valuation_keeps_dcf_unavailable_without_cash_flow_data():
    data = pd.DataFrame(
        [{
            "Preco_Atual": 20.0,
            "PL": 10.0,
            "PVP": 2.0,
            "Dividend_Yield_%": 6.0,
        }]
    )

    result = calculate_valuation(data)

    assert pd.isna(result.loc[0, "Preco_Justo_DCF"])
    assert pd.isna(result.loc[0, "Margem_DCF_%"])
