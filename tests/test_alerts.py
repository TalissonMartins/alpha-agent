import pandas as pd

from src.opportunities.alerts import extrair_alertas, filtrar_novos


def test_extrai_somente_zona_compra():
    df = pd.DataFrame(
        [
            {
                "Ticker": "PETR4",
                "Preco_Atual": 30.0,
                "Preco_Justo_Graham": 40.0,
                "Margem_Graham_%": 25.0,
                "Status_Graham": "ZONA_COMPRA",
                "Preco_Justo_Gordon": 20.0,
                "Status_Gordon": "CARO",
            },
            {
                "Ticker": "WEGE3",
                "Preco_Atual": 50.0,
                "Preco_Justo_Graham": 12.0,
                "Margem_Graham_%": -300.0,
                "Status_Graham": "CARO",
                "Preco_Justo_Gordon": 19.0,
                "Status_Gordon": "CARO",
            },
        ]
    )
    alertas = extrair_alertas(df)
    assert len(alertas) == 1
    assert alertas.loc[0, "ticker"] == "PETR4"
    assert alertas.loc[0, "modelo"] == "GRAHAM"


def test_sem_zona_compra_devolve_tabela_vazia():
    df = pd.DataFrame(
        [
            {
                "Ticker": "VALE3",
                "Preco_Atual": 70.0,
                "Preco_Justo_Graham": 50.0,
                "Margem_Graham_%": -40.0,
                "Status_Graham": "CARO",
                "Preco_Justo_Gordon": 40.0,
                "Status_Gordon": "CARO",
            }
        ]
    )
    alertas = extrair_alertas(df)
    assert alertas.empty
    assert "ticker" in alertas.columns


def test_nao_repete_zona_compra_da_rodada_anterior():
    atual = pd.DataFrame(
        [
            {
                "Ticker": "PETR4",
                "Preco_Atual": 30.0,
                "Preco_Justo_Graham": 40.0,
                "Margem_Graham_%": 25.0,
                "Status_Graham": "ZONA_COMPRA",
                "Preco_Justo_Gordon": 50.0,
                "Status_Gordon": "ZONA_COMPRA",
            }
        ]
    )
    anterior = pd.DataFrame(
        [
            {
                "Ticker": "PETR4",
                "Status_Graham": "ZONA_COMPRA",
                "Status_Gordon": "OBSERVAR",
            }
        ]
    )
    novos = filtrar_novos(atual, anterior)
    assert len(novos) == 1
    assert novos.loc[0, "modelo"] == "GORDON"
