from typing import Any

import pandas as pd

INDEXADORES = ("IPCA", "PREFIXADO", "CDI")


def calcular_renda_fixa(carteira: dict, referencias: dict) -> pd.DataFrame:
    """Classifica a taxa contratada contra a referencia. Nao emite ordem."""
    limiar = float(referencias.get("limiar_spread", 0.0))
    linhas: list[dict[str, Any]] = []
    for posicao in carteira.get("posicoes", []):
        if str(posicao.get("classe", "")).upper() != "RF_BR":
            continue
        linhas.append(_linha(posicao, referencias, limiar))
    colunas = [
        "nome",
        "indexador",
        "taxa_contratada_%",
        "taxa_referencia_%",
        "spread_pp",
        "prazo_anos",
        "valor_brl",
        "valor_projetado_brl",
        "status_rf",
    ]
    if not linhas:
        return pd.DataFrame(columns=colunas)
    return pd.DataFrame(linhas, columns=colunas)


def _linha(posicao: dict, referencias: dict, limiar: float) -> dict[str, Any]:
    nome = posicao.get("nome") or posicao.get("ticker") or "N/A"
    indexador = str(posicao.get("indexador", "")).upper()
    taxa = _num(posicao.get("taxa_aa"))
    prazo = _num(posicao.get("prazo_anos"))
    valor = _num(posicao.get("valor_brl"))
    referencia = _referencia(indexador, referencias)
    if indexador not in INDEXADORES or taxa is None or referencia is None:
        return {
            "nome": nome,
            "indexador": indexador or "N/A",
            "taxa_contratada_%": taxa,
            "taxa_referencia_%": referencia,
            "spread_pp": None,
            "prazo_anos": prazo,
            "valor_brl": valor,
            "valor_projetado_brl": None,
            "status_rf": "INCOMPLETO",
        }
    spread = round(taxa - referencia, 4)
    if spread >= limiar:
        status = "ACIMA_REFERENCIA"
    elif spread >= 0:
        status = "NA_REFERENCIA"
    else:
        status = "ABAIXO_REFERENCIA"
    return {
        "nome": nome,
        "indexador": indexador,
        "taxa_contratada_%": taxa,
        "taxa_referencia_%": referencia,
        "spread_pp": spread,
        "prazo_anos": prazo,
        "valor_brl": valor,
        "valor_projetado_brl": _projetar(indexador, valor, taxa, prazo, referencias),
        "status_rf": status,
    }


def _referencia(indexador: str, referencias: dict) -> float | None:
    chave = {
        "IPCA": "ipca_mais_mercado",
        "PREFIXADO": "prefixado_mercado",
        "CDI": "cdi_mais_mercado",
    }.get(indexador)
    if chave is None:
        return None
    return _num(referencias.get(chave))


def _projetar(
    indexador: str,
    valor: float | None,
    taxa: float,
    prazo: float | None,
    referencias: dict,
) -> float | None:
    if valor is None or prazo is None or prazo <= 0:
        return None
    taxa_decimal = taxa / 100
    if indexador == "PREFIXADO":
        fator = (1 + taxa_decimal) ** prazo
    elif indexador == "IPCA":
        ipca = _num(referencias.get("ipca_aa"))
        if ipca is None:
            return None
        fator = ((1 + ipca / 100) * (1 + taxa_decimal)) ** prazo
    else:
        cdi = _num(referencias.get("cdi_aa"))
        if cdi is None:
            return None
        fator = (1 + (cdi + taxa) / 100) ** prazo
    return round(valor * fator, 2)


def _num(value: object) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
