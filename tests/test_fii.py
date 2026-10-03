import pandas as pd

from src.portfolio.fii import classificar_fii


def test_pvp_abaixo_de_um_e_desconto():
    df = classificar_fii(pd.DataFrame([{"Ticker": "HGLG11", "PVP": 0.92}]))
    assert df.loc[0, "Status_FII"] == "DESCONTO"


def test_pvp_acima_de_um_e_premio():
    df = classificar_fii(pd.DataFrame([{"Ticker": "XPML11", "PVP": 1.08}]))
    assert df.loc[0, "Status_FII"] == "PREMIO"


def test_pvp_ausente_fica_incompleto():
    df = classificar_fii(pd.DataFrame([{"Ticker": "MXRF11", "PVP": None}]))
    assert df.loc[0, "Status_FII"] == "INCOMPLETO"
