from pathlib import Path

import pandas as pd


def gravar_carteira_html(
    alocacao: pd.DataFrame,
    renda_fixa: pd.DataFrame,
    exterior: pd.DataFrame,
    fiis: pd.DataFrame,
    destino: Path,
) -> None:
    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <title>AlphaAgent — carteira interna</title>
  <style>
    body {{ font-family: sans-serif; background: #111; color: #eee; margin: 24px; }}
    h1, h2 {{ font-weight: 600; }}
    p {{ color: #aaa; }}
    table {{ border-collapse: collapse; width: 100%; margin-bottom: 24px; }}
    th, td {{ border-bottom: 1px solid #333; padding: 8px; text-align: right; }}
    th:first-child, td:first-child {{ text-align: left; }}
  </style>
</head>
<body>
  <h1>AlphaAgent — carteira interna</h1>
  <p>Classificacao. Nao e ordem de compra nem de venda.</p>
  <h2>Alocacao</h2>
  {alocacao.to_html(index=False, border=0)}
  <h2>Renda fixa</h2>
  {renda_fixa.to_html(index=False, border=0)}
  <h2>Fundos imobiliarios</h2>
  {fiis.to_html(index=False, border=0)}
  <h2>Exterior em dolar</h2>
  {exterior.to_html(index=False, border=0)}
</body>
</html>
"""
    destino.write_text(html, encoding="utf-8")
