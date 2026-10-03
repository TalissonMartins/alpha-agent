import pytest

from src.portfolio.alocacao import resumo_alocacao


def test_soma_as_tres_classes_em_brl():
    carteira = {
        "usdbrl": 5.0,
        "posicoes": [
            {"classe": "RV_BR", "ticker": "PETR4", "valor_brl": 1000},
            {"classe": "RF_BR", "nome": "Tesouro", "valor_brl": 1000},
            {"classe": "RV_USD", "ticker": "AAPL", "valor_usd": 200},
        ],
    }
    resumo = resumo_alocacao(carteira)
    total = resumo["valor_brl"].sum()
    assert total == 3000
    assert set(resumo["classe"]) == {"RV_BR", "RF_BR", "RV_USD"}
    assert resumo["peso_%"].sum() == pytest.approx(100, abs=0.05)


def test_rejeita_classe_desconhecida():
    carteira = {
        "usdbrl": 5.0,
        "posicoes": [{"classe": "CRIPTO", "nome": "BTC", "valor_brl": 10}],
    }
    with pytest.raises(ValueError):
        resumo_alocacao(carteira)
