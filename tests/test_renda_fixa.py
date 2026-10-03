from src.portfolio.renda_fixa import calcular_renda_fixa

REFERENCIAS = {
    "ipca_aa": 4.5,
    "ipca_mais_mercado": 6.0,
    "prefixado_mercado": 12.5,
    "cdi_aa": 13.0,
    "cdi_mais_mercado": 0.0,
    "limiar_spread": 0.20,
}


def test_ipca_acima_da_referencia():
    carteira = {
        "posicoes": [
            {
                "classe": "RF_BR",
                "nome": "Tesouro IPCA+",
                "indexador": "IPCA",
                "taxa_aa": 6.5,
                "prazo_anos": 2,
                "valor_brl": 1000,
            }
        ]
    }
    df = calcular_renda_fixa(carteira, REFERENCIAS)
    assert df.loc[0, "status_rf"] == "ACIMA_REFERENCIA"
    assert df.loc[0, "spread_pp"] == 0.5
    assert df.loc[0, "valor_projetado_brl"] is not None


def test_prefixado_abaixo_da_referencia():
    carteira = {
        "posicoes": [
            {
                "classe": "RF_BR",
                "nome": "Tesouro Prefixado",
                "indexador": "PREFIXADO",
                "taxa_aa": 11.0,
                "prazo_anos": 2,
                "valor_brl": 1000,
            }
        ]
    }
    df = calcular_renda_fixa(carteira, REFERENCIAS)
    assert df.loc[0, "status_rf"] == "ABAIXO_REFERENCIA"


def test_posicao_sem_indexador_fica_incompleta():
    carteira = {"posicoes": [{"classe": "RF_BR", "nome": "CDB", "valor_brl": 500}]}
    df = calcular_renda_fixa(carteira, REFERENCIAS)
    assert df.loc[0, "status_rf"] == "INCOMPLETO"


def test_ignora_acao_e_dolar():
    carteira = {
        "posicoes": [
            {"classe": "RV_BR", "ticker": "PETR4", "valor_brl": 10},
            {"classe": "RV_USD", "ticker": "AAPL", "valor_usd": 10},
        ]
    }
    df = calcular_renda_fixa(carteira, REFERENCIAS)
    assert df.empty
