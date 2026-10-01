import logging

from .data.data_fetcher import fetch_multiple_tickers
from .finance.engine import calculate_valuation
from .opportunities.evaluator import RuleEvaluator
from .opportunities.schemas import OpportunityRuleSchema, ValuationModelEnum

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("AlphaAgent-Main")

COLUNAS = [
    "Ticker",
    "Preco_Atual",
    "PL",
    "PVP",
    "Dividend_Yield_%",
    "Preco_Justo_Graham",
    "Margem_Graham_%",
    "Earnings_Yield_%",
    "Preco_Justo_Gordon",
    "Status_Regra",
]


def _status_graham(row, evaluator: RuleEvaluator) -> str:
    rule = OpportunityRuleSchema(
        ticker=str(row.get("Ticker", "N/A")),
        valuation_model=ValuationModelEnum.GRAHAM,
        limiar_compra=0.20,
    )
    resultado = evaluator.evaluate(
        rule,
        current_price=row.get("Preco_Atual"),
        fair_value=row.get("Preco_Justo_Graham"),
    )
    return resultado.status.value


def main() -> None:
    logger.info("Iniciando o AlphaAgent - Orquestrador (Fase 3.1)")
    watchlist_b3 = ["PETR4.SA", "VALE3.SA", "ITUB4.SA", "WEGE3.SA"]

    logger.info("Acionando o modulo de extracao de dados...")
    try:
        df_raw = fetch_multiple_tickers(watchlist_b3)
    except Exception as exc:
        logger.error("Falha na coleta de dados: %s", exc)
        return

    if df_raw.empty:
        logger.error("Nenhum dado retornado na extracao.")
        return

    logger.info("Acionando o Motor Financeiro...")
    try:
        df_final = calculate_valuation(df_raw)
    except Exception as exc:
        logger.error("Falha no calculo do motor financeiro: %s", exc)
        return

    evaluator = RuleEvaluator()
    df_final["Status_Regra"] = df_final.apply(
        lambda row: _status_graham(row, evaluator), axis=1
    )

    presentes = [coluna for coluna in COLUNAS if coluna in df_final.columns]
    faltando = [coluna for coluna in COLUNAS if coluna not in df_final.columns]

    print("\n" + "=" * 125)
    print("         ALPHAAGENT - RELATORIO DE VALUATION + STATUS (FASE 3.1)")
    print("=" * 125)
    print(df_final[presentes].to_string(index=False))
    print("=" * 125)
    if faltando:
        logger.warning("Colunas ausentes no DataFrame: %s", faltando)


if __name__ == "__main__":
    main()
