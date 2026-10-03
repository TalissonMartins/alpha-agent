import json
from pathlib import Path

import pandas as pd

CLASSES = ("RV_BR", "RF_BR", "RV_USD", "FII_BR")


def carregar_carteira(path: Path) -> dict:
    dados = json.loads(path.read_text(encoding="utf-8"))
    if "usdbrl" not in dados or "posicoes" not in dados:
        raise ValueError("carteira.json precisa de usdbrl e posicoes")
    return dados


def resumo_alocacao(carteira: dict) -> pd.DataFrame:
    """Soma valor em BRL por classe. Nao calcula valuation de RF nem de ativo em dolar."""
    cambio = float(carteira["usdbrl"])
    if cambio <= 0:
        raise ValueError("usdbrl invalido")

    linhas = []
    for posicao in carteira["posicoes"]:
        classe = str(posicao.get("classe", "")).upper()
        if classe not in CLASSES:
            raise ValueError(f"Classe desconhecida: {classe}")
        valor_brl = posicao.get("valor_brl")
        valor_usd = posicao.get("valor_usd")
        if valor_brl is None and valor_usd is None:
            raise ValueError(f"Posicao sem valor: {posicao.get('nome') or posicao.get('ticker')}")
        if valor_brl is None:
            valor_brl = float(valor_usd) * cambio
        linhas.append({"classe": classe, "valor_brl": float(valor_brl)})

    df = pd.DataFrame(linhas)
    if df.empty:
        return pd.DataFrame(columns=["classe", "valor_brl", "peso_%"])
    resumo = df.groupby("classe", as_index=False)["valor_brl"].sum()
    total = resumo["valor_brl"].sum()
    resumo["peso_%"] = (resumo["valor_brl"] / total * 100).round(2)
    resumo["valor_brl"] = resumo["valor_brl"].round(2)
    return resumo.sort_values("classe").reset_index(drop=True)
