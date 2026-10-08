from pathlib import Path

import pandas as pd

COR = {
    "ZONA_COMPRA": "ok",
    "DESCONTO": "ok",
    "ACIMA_REFERENCIA": "ok",
    "OBSERVAR": "alerta",
    "NA_REFERENCIA": "alerta",
    "CARO": "risco",
    "ABAIXO_REFERENCIA": "risco",
    "PREMIO": "risco",
}


def gravar_carteira_html(
    alocacao: pd.DataFrame,
    renda_fixa: pd.DataFrame,
    exterior: pd.DataFrame,
    fiis: pd.DataFrame,
    destino: Path,
    acoes: pd.DataFrame | None = None,
) -> None:
    destino.write_text(
        _pagina(alocacao, renda_fixa, exterior, fiis, acoes if acoes is not None else pd.DataFrame()),
        encoding="utf-8",
    )


def _pagina(alocacao, renda_fixa, exterior, fiis, acoes) -> str:
    return """<!DOCTYPE html>
<html lang=\"pt-BR\">
<head>
  <meta charset=\"utf-8\">
  <title>AlphaAgent</title>
  <style>
    body { margin: 0; background: #0c1117; color: #e8e6e3; font-family: sans-serif; }
    header, main { padding: 28px 40px; }
    h1 span, h2 { color: #c4a46a; }
    section { background: #161d27; border: 1px solid #263140; border-radius: 12px; padding: 18px; margin-bottom: 22px; }
    table { width: 100%; border-collapse: collapse; }
    th, td { padding: 8px; text-align: right; border-top: 1px solid #263140; }
    th:first-child, td:first-child { text-align: left; }
    .ok { color: #8ed7b3; } .alerta { color: #e4c27a; } .risco { color: #e3a19b; }
  </style>
</head>
<body>
  <header><h1>Alpha<span>Agent</span></h1><p>Classificacao. Nao e ordem de compra nem de venda.</p></header>
  <main>
    <section><h2>Alocacao</h2>__ALOCACAO__</section>
    <section><h2>Acoes B3</h2>__ACOES__</section>
    <section><h2>Renda fixa</h2>__RF__</section>
    <section><h2>Fundos imobiliarios</h2>__FII__</section>
    <section><h2>Exterior em dolar</h2>__USD__</section>
  </main>
</body>
</html>
""".replace("__ALOCACAO__", _alocacao(alocacao)).replace("__ACOES__", _tabela(acoes)).replace("__RF__", _tabela(renda_fixa)).replace("__FII__", _tabela(fiis)).replace("__USD__", _tabela(exterior))


def _alocacao(df: pd.DataFrame) -> str:
    if df.empty:
        return "<p>Sem posicoes.</p>"
    linhas = []
    for _, row in df.iterrows():
        peso = float(row.get("peso_%") or 0)
        linhas.append(f"<tr><td>{row.get('classe')}</td><td>{row.get('valor_brl')}</td><td>{peso:.2f}</td></tr>")
    return "<table><tr><th>Classe</th><th>Valor em R$</th><th>Peso %</th></tr>" + "".join(linhas) + "</table>"


def _tabela(df: pd.DataFrame) -> str:
    if df is None or df.empty:
        return "<p>Sem dados nesta classe.</p>"
    cabeca = "".join(f"<th>{coluna}</th>" for coluna in df.columns)
    corpo = []
    for _, row in df.iterrows():
        celulas = []
        for valor in row:
            texto = "" if valor is None else str(valor)
            classe = COR.get(texto)
            celulas.append(f"<td class='{classe}'>{texto}</td>" if classe else f"<td>{texto}</td>")
        corpo.append("<tr>" + "".join(celulas) + "</tr>")
    return f"<table><tr>{cabeca}</tr>{''.join(corpo)}</table>"
