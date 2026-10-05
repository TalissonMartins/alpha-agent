from datetime import date

import pandas as pd

from src.portfolio.historico import acumular, linhas_do_dia


def test_grava_graham_e_gordon_no_dia():
    acoes = pd.DataFrame(
        [{"Ticker": "PETR4", "Preco_Atual": 50.0, "Status_Graham": "ZONA_COMPRA", "Status_Gordon": "OBSERVAR"}]
    )
    linhas = linhas_do_dia(acoes, pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), date(2026, 10, 5))
    assert len(linhas) == 2
    assert set(linhas["modelo"]) == {"GRAHAM", "GORDON"}
    assert linhas.loc[0, "data"] == "2026-10-05"


def test_segunda_rodada_do_mesmo_dia_nao_duplica():
    novas = pd.DataFrame(
        [
            {
                "data": "2026-10-05",
                "classe": "RV_BR",
                "ativo": "PETR4",
                "modelo": "GRAHAM",
                "preco": 51.0,
                "status": "ZONA_COMPRA",
            }
        ]
    )
    primeira = novas.copy()
    primeira.loc[0, "preco"] = 50.0
    historico = acumular(primeira, novas)
    assert len(historico) == 1
    assert historico.loc[0, "preco"] == 51.0
