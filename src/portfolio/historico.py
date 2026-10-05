from datetime import date

import pandas as pd

COLUNAS = ("data", "classe", "ativo", "modelo", "preco", "status")


def linhas_do_dia(
    acoes: pd.DataFrame,
    fiis: pd.DataFrame,
    exterior: pd.DataFrame,
    renda_fixa: pd.DataFrame,
    hoje: date | None = None,
) -> pd.DataFrame:
    dia = (hoje or date.today()).isoformat()
    linhas: list[dict] = []
    linhas.extend(_pares(acoes, "RV_BR", "Ticker", "Preco_Atual", dia))
    linhas.extend(_pares(exterior, "RV_USD", "Ticker", "Preco_Atual", dia))
    for _, row in fiis.iterrows():
        linhas.append(
            {
                "data": dia,
                "classe": "FII_BR",
                "ativo": row.get("Ticker"),
                "modelo": "PVP",
                "preco": row.get("Preco_Atual"),
                "status": row.get("Status_FII"),
            }
        )
    for _, row in renda_fixa.iterrows():
        linhas.append(
            {
                "data": dia,
                "classe": "RF_BR",
                "ativo": row.get("nome"),
                "modelo": row.get("indexador"),
                "preco": row.get("valor_brl"),
                "status": row.get("status_rf"),
            }
        )
    if not linhas:
        return pd.DataFrame(columns=list(COLUNAS))
    return pd.DataFrame(linhas, columns=list(COLUNAS))


def acumular(anterior: pd.DataFrame | None, novas: pd.DataFrame) -> pd.DataFrame:
    """Um registro por data, classe, ativo e modelo. O do dia e substituido."""
    if novas.empty:
        return anterior if anterior is not None else pd.DataFrame(columns=list(COLUNAS))
    base = anterior if anterior is not None and not anterior.empty else pd.DataFrame(columns=list(COLUNAS))
    chaves = ["data", "classe", "ativo", "modelo"]
    if base.empty:
        return novas
    juntos = pd.concat([base, novas], ignore_index=True)
    return juntos.drop_duplicates(chaves, keep="last").reset_index(drop=True)


def _pares(df: pd.DataFrame, classe: str, coluna_ativo: str, coluna_preco: str, dia: str) -> list[dict]:
    linhas = []
    if df is None or df.empty:
        return linhas
    for _, row in df.iterrows():
        for modelo, coluna in (("GRAHAM", "Status_Graham"), ("GORDON", "Status_Gordon")):
            if coluna not in df.columns:
                continue
            linhas.append(
                {
                    "data": dia,
                    "classe": classe,
                    "ativo": row.get(coluna_ativo),
                    "modelo": modelo,
                    "preco": row.get(coluna_preco),
                    "status": row.get(coluna),
                }
            )
    return linhas
