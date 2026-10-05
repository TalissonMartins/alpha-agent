import pandas as pd


def mudancas_de_status(historico: pd.DataFrame) -> pd.DataFrame:
    """Compara os dois ultimos dias. Sem o segundo dia, devolve vazio."""
    colunas = ["ativo", "classe", "modelo", "status_anterior", "status_atual"]
    if historico.empty or "data" not in historico.columns:
        return pd.DataFrame(columns=colunas)
    dias = sorted(historico["data"].astype(str).unique())
    if len(dias) < 2:
        return pd.DataFrame(columns=colunas)
    anterior = historico[historico["data"].astype(str) == dias[-2]]
    atual = historico[historico["data"].astype(str) == dias[-1]]
    chaves = ["classe", "ativo", "modelo"]
    juntos = anterior.merge(atual, on=chaves, suffixes=("_anterior", "_atual"))
    mudou = juntos[juntos["status_anterior"] != juntos["status_atual"]]
    if mudou.empty:
        return pd.DataFrame(columns=colunas)
    return mudou[colunas].reset_index(drop=True)
