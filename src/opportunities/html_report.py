from pathlib import Path

import pandas as pd


def gravar_html(df: pd.DataFrame, destino: Path) -> None:
    tabela = df.to_html(index=False, border=0, classes="tabela")
    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <title>AlphaAgent — relatorio interno</title>
  <style>
    body {{ font-family: sans-serif; background: #111; color: #eee; margin: 24px; }}
    h1 {{ font-size: 20px; }}
    p {{ color: #aaa; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border-bottom: 1px solid #333; padding: 8px; text-align: right; }}
    th:first-child, td:first-child {{ text-align: left; }}
  </style>
</head>
<body>
  <h1>AlphaAgent — relatorio interno</h1>
  <p>Classificacao de margem. Nao e ordem de compra nem de venda.</p>
  {tabela}
</body>
</html>
"""
    destino.write_text(html, encoding="utf-8")
