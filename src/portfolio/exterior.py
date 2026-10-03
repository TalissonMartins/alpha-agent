import pandas as pd


def tickers_usd(carteira: dict) -> list[str]:
    tickers = []
    for posicao in carteira.get("posicoes", []):
        if str(posicao.get("classe", "")).upper() != "RV_USD":
            continue
        ticker = str(posicao.get("ticker", "")).strip().upper()
        if ticker:
            tickers.append(ticker)
    return tickers


def adicionar_preco_brl(df: pd.DataFrame, usdbrl: float) -> pd.DataFrame:
    if usdbrl <= 0:
        raise ValueError("usdbrl invalido")
    out = df.copy()
    out["Preco_BRL"] = [
        round(float(preco) * usdbrl, 2) if preco is not None and preco == preco else None
        for preco in out.get("Preco_Atual", [])
    ]
    return out
