from datetime import datetime, timezone

import pandas as pd

COLUNAS_ALERTA = (
    "registrado_em",
    "ticker",
    "modelo",
    "status",
    "preco_atual",
    "valor_justo",
    "margem_%",
)


def extrair_alertas(df: pd.DataFrame, agora: datetime | None = None) -> pd.DataFrame:
    """Registra classificacao ZONA_COMPRA. Nao emite ordem."""
    momento = (agora or datetime.now(timezone.utc)).strftime("%Y-%m-%dT%H:%M:%SZ")
    linhas: list[dict] = []
    pares = (
        ("GRAHAM", "Status_Graham", "Preco_Justo_Graham", "Margem_Graham_%"),
        ("GORDON", "Status_Gordon", "Preco_Justo_Gordon", None),
    )
    for _, row in df.iterrows():
        for modelo, coluna_status, coluna_justo, coluna_margem in pares:
            if row.get(coluna_status) != "ZONA_COMPRA":
                continue
            margem = row.get(coluna_margem) if coluna_margem else None
            linhas.append(
                {
                    "registrado_em": momento,
                    "ticker": row.get("Ticker"),
                    "modelo": modelo,
                    "status": "ZONA_COMPRA",
                    "preco_atual": row.get("Preco_Atual"),
                    "valor_justo": row.get(coluna_justo),
                    "margem_%": margem,
                }
            )
    if not linhas:
        return pd.DataFrame(columns=list(COLUNAS_ALERTA))
    return pd.DataFrame(linhas, columns=list(COLUNAS_ALERTA))


def filtrar_novos(atual: pd.DataFrame, anterior: pd.DataFrame | None) -> pd.DataFrame:
    """So registra ZONA_COMPRA que nao estava nesse status na rodada anterior."""
    correntes = extrair_alertas(atual)
    if correntes.empty or anterior is None or anterior.empty:
        return correntes

    ja_estava: set[tuple[str, str]] = set()
    mapa = (("GRAHAM", "Status_Graham"), ("GORDON", "Status_Gordon"))
    for _, row in anterior.iterrows():
        ticker = str(row.get("Ticker"))
        for modelo, coluna in mapa:
            if row.get(coluna) == "ZONA_COMPRA":
                ja_estava.add((ticker, modelo))

    mascara = [
        (str(row.ticker), str(row.modelo)) not in ja_estava
        for row in correntes.itertuples(index=False)
    ]
    return correntes.loc[mascara].reset_index(drop=True)
