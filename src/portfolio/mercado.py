import csv
import json
from datetime import datetime
from io import StringIO
from urllib.request import Request, urlopen

import yfinance as yf

BCB = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados/ultimos/{n}?formato=json"
TESOURO = (
    "https://www.tesourotransparente.gov.br/ckan/dataset/"
    "df56aa42-484a-4a59-8184-7676580c81e3/resource/"
    "796d2059-14e9-44e3-80c9-2d9e30b405c1/download/PrecoTaxaTesouroDireto.csv"
)


def cotacao_usdbrl(manual: float) -> tuple[float, str]:
    try:
        info = yf.Ticker("USDBRL=X").info
        preco = info.get("regularMarketPrice") or info.get("bid")
        valor = float(preco)
        if valor <= 0:
            raise ValueError("cotacao invalida")
        return round(valor, 4), "yahoo"
    except Exception:
        return float(manual), "manual"


def ipca_12m(valores_mensais: list[float]) -> float:
    fator = 1.0
    for valor in valores_mensais[-12:]:
        fator *= 1 + float(valor) / 100
    return round((fator - 1) * 100, 2)


def atualizar_referencias(base: dict, ano_alvo: int = 2029) -> tuple[dict, str]:
    saida = dict(base)
    origem = "manual"
    try:
        selic = _ultimo(432)
        ipca = ipca_12m(_serie(433, 12))
        if selic is not None:
            saida["cdi_aa"] = selic
            saida["prefixado_mercado"] = selic
            origem = "bcb"
        if ipca is not None:
            saida["ipca_aa"] = ipca
            origem = "bcb"
    except Exception:
        pass
    try:
        taxa = detalhe_ipca_mais(ano_alvo)
        if taxa is not None:
            saida["ipca_mais_mercado"] = taxa["taxa"]
            saida["titulo_referencia"] = taxa["titulo"]
            saida["vencimento_referencia"] = taxa["vencimento"]
            saida["data_referencia"] = taxa["data_base"]
            origem = "tesouro"
    except Exception:
        pass
    return saida, origem


def detalhe_ipca_mais(ano_alvo: int) -> dict | None:
    req = Request(TESOURO, headers={"User-Agent": "AlphaAgent/3.14"})
    with urlopen(req, timeout=15) as resposta:
        texto = resposta.read().decode("latin-1")
    return escolher_ipca_mais(texto, ano_alvo)


def escolher_ipca_mais(texto: str, ano_alvo: int) -> dict | None:
    linhas = list(csv.DictReader(StringIO(texto), delimiter=";"))
    ipca = [linha for linha in linhas if linha.get("Tipo Titulo") == "Tesouro IPCA+"]
    if not ipca:
        return None
    ultima = max(ipca, key=lambda linha: _data(linha["Data Base"]))
    do_dia = [linha for linha in ipca if linha["Data Base"] == ultima["Data Base"]]
    vigentes = [linha for linha in do_dia if _data(linha["Data Vencimento"]) >= _data(linha["Data Base"])]
    if not vigentes:
        return None
    escolhida = min(vigentes, key=lambda linha: abs(_ano(linha["Data Vencimento"]) - ano_alvo))
    return {
        "titulo": escolhida["Tipo Titulo"],
        "vencimento": escolhida["Data Vencimento"],
        "data_base": escolhida["Data Base"],
        "taxa": round(float(escolhida["Taxa Compra Manha"].replace(",", ".")), 2),
    }


def _data(texto: str) -> datetime:
    return datetime.strptime(texto, "%d/%m/%Y")


def _ano(data: str) -> int:
    return int(data.split("/")[-1])


def _serie(codigo: int, n: int) -> list[float]:
    with urlopen(BCB.format(codigo=codigo, n=n), timeout=8) as resposta:
        dados = json.loads(resposta.read().decode("utf-8"))
    return [float(str(item["valor"]).replace(",", ".")) for item in dados]


def _ultimo(codigo: int) -> float | None:
    valores = _serie(codigo, 1)
    return round(valores[-1], 2) if valores else None
