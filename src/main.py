import json
import logging
from pathlib import Path

import pandas as pd

from .data.data_fetcher import fetch_multiple_tickers
from .finance.engine import calculate_valuation
from .opportunities.evaluator import RuleEvaluator
from .opportunities.schemas import OpportunityRuleSchema, ValuationModelEnum

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("AlphaAgent-Main")

ROOT = Path(__file__).resolve().parents[1]
COLUNAS = [
    "Ticker",
    "Preco_Atual",
    "PL",
    "PVP",
    "Dividend_Yield_%",
    "Preco_Justo_Graham",
    "Margem_Graham_%",
    "Status_Graham",
    "Earnings_Yield_%",
    "Preco_Justo_Gordon",
    "Status_Gordon",
]


def carregar_watchlist(path: Path) -> list[str]:
    linhas = path.read_text(encoding="utf-8").splitlines()
    tickers = [linha.strip().upper() for linha in linhas if linha.strip() and not linha.startswith("#")]
    if not tickers:
        raise ValueError(f"Watchlist vazia: {path}")
    return tickers


def carregar_limiar(path: Path) -> float:
    dados = json.loads(path.read_text(encoding="utf-8"))
    return float(dados["limiar_compra"])


def classificar(df: pd.DataFrame, limiar: float, evaluator: RuleEvaluator) -> pd.DataFrame:
    out = df.copy()

    def status(row: pd.Series, modelo: ValuationModelEnum, coluna_justo: str) -> str:
        rule = OpportunityRuleSchema(
            ticker=str(row.get("Ticker", "N/A")),
            valuation_model=modelo,
            limiar_compra=limiar,
        )
        resultado = evaluator.evaluate(
            rule,
            current_price=row.get("Preco_Atual"),
            fair_value=row.get(coluna_justo),
        )
        return resultado.status.value

    out["Status_Graham"] = out.apply(
        lambda row: status(row, ValuationModelEnum.GRAHAM, "Preco_Justo_Graham"),
        axis=1,
    )
    out["Status_Gordon"] = out.apply(
        lambda row: status(row, ValuationModelEnum.GORDON, "Preco_Justo_Gordon"),
        axis=1,
    )
    return out


def main() -> None:
    logger.info("Iniciando o AlphaAgent - Orquestrador (Fase 3.1)")
    watchlist = carregar_watchlist(ROOT / "config" / "watchlist.txt")
    limiar = carregar_limiar(ROOT / "config" / "regras.json")
    logger.info("Watchlist: %s | limiar: %.0f%%", watchlist, limiar * 100)

    try:
        df_raw = fetch_multiple_tickers(watchlist)
    except Exception as exc:
        logger.error("Falha na coleta de dados: %s", exc)
        return
    if df_raw.empty:
        logger.error("Nenhum dado retornado na extracao.")
        return

    try:
        df_final = calculate_valuation(df_raw)
        df_final = classificar(df_final, limiar, RuleEvaluator())
    except Exception as exc:
        logger.error("Falha no calculo do motor financeiro: %s", exc)
        return

    presentes = [coluna for coluna in COLUNAS if coluna in df_final.columns]
    faltando = [coluna for coluna in COLUNAS if coluna not in df_final.columns]
    relatorio = ROOT / "relatorios" / "ultimo.csv"
    relatorio.parent.mkdir(exist_ok=True)
    df_final[presentes].to_csv(relatorio, index=False)

    print("\n" + "=" * 140)
    print("         ALPHAAGENT - RELATORIO DE VALUATION + STATUS (FASE 3.1)")
    print("=" * 140)
    print(df_final[presentes].to_string(index=False))
    print("=" * 140)
    logger.info("CSV gravado em %s", relatorio)
    if faltando:
        logger.warning("Colunas ausentes no DataFrame: %s", faltando)


if __name__ == "__main__":
    main()
