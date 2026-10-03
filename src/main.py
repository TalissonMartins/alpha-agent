import json
import logging
from pathlib import Path

import pandas as pd

from .data.data_fetcher import fetch_multiple_tickers
from .finance.engine import calculate_valuation
from .opportunities.alerts import extrair_alertas, filtrar_novos
from .opportunities.evaluator import RuleEvaluator
from .opportunities.html_report import gravar_html
from .opportunities.schemas import OpportunityRuleSchema, ValuationModelEnum
from .portfolio.alocacao import carregar_carteira, resumo_alocacao
from .portfolio.consolidado import gravar_carteira_html
from .portfolio.exterior import adicionar_preco_brl, tickers_usd
from .portfolio.fii import classificar_fii
from .portfolio.renda_fixa import calcular_renda_fixa

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
    logger.info("Iniciando o AlphaAgent - Orquestrador (Fase 3.8)")
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
    html = ROOT / "relatorios" / "ultimo.html"
    alertas_path = ROOT / "relatorios" / "alertas.csv"
    anterior_path = ROOT / "relatorios" / "anterior.csv"
    relatorio.parent.mkdir(exist_ok=True)
    anterior = pd.read_csv(anterior_path) if anterior_path.exists() else None
    novos = filtrar_novos(df_final, anterior)
    if alertas_path.exists() and not novos.empty:
        pd.concat([pd.read_csv(alertas_path), novos], ignore_index=True).to_csv(
            alertas_path, index=False
        )
    elif not alertas_path.exists():
        novos.to_csv(alertas_path, index=False)
    df_final[presentes].to_csv(relatorio, index=False)
    df_final[presentes].to_csv(anterior_path, index=False)
    gravar_html(df_final[presentes], html)

    print("\n" + "=" * 140)
    print("         ALPHAAGENT - RELATORIO DE VALUATION + STATUS (FASE 3.5)")
    print("=" * 140)
    print(df_final[presentes].to_string(index=False))
    print("=" * 140)
    logger.info("CSV gravado em %s", relatorio)
    logger.info("HTML gravado em %s", html)
    logger.info("Alertas novos: %d linha(s) em %s", len(novos), alertas_path)
    if faltando:
        logger.warning("Colunas ausentes no DataFrame: %s", faltando)

    carteira = carregar_carteira(ROOT / "config" / "carteira.json")
    alocacao = resumo_alocacao(carteira)
    alocacao_path = ROOT / "relatorios" / "alocacao.csv"
    alocacao.to_csv(alocacao_path, index=False)
    print("\n" + "=" * 80)
    print("         ALPHAAGENT - ALOCACAO DA CARTEIRA")
    print("         RV_USD calculada no bloco exterior.")
    print("=" * 80)
    print(alocacao.to_string(index=False))
    print("=" * 80)
    logger.info("Alocacao gravada em %s", alocacao_path)

    referencias = json.loads((ROOT / "config" / "referencias_rf.json").read_text(encoding="utf-8"))
    renda_fixa = calcular_renda_fixa(carteira, referencias)
    rf_path = ROOT / "relatorios" / "renda_fixa.csv"
    renda_fixa.to_csv(rf_path, index=False)
    print("\n" + "=" * 110)
    print("         ALPHAAGENT - RENDA FIXA (FASE 3.5)")
    print("         Compara taxa contratada com a referencia. Nao e ordem.")
    print("=" * 110)
    print(renda_fixa.to_string(index=False))
    print("=" * 110)
    logger.info("Renda fixa gravada em %s", rf_path)

    colunas_usd = ["Ticker", "Preco_Atual", "Preco_BRL", "Preco_Justo_Graham", "Status_Graham", "Status_Gordon"]
    df_usd = pd.DataFrame(columns=colunas_usd)
    tickers = tickers_usd(carteira)
    if tickers:
        try:
            bruto = fetch_multiple_tickers(tickers)
            if not bruto.empty:
                avaliado = classificar(calculate_valuation(bruto), limiar, RuleEvaluator())
                df_usd = adicionar_preco_brl(avaliado, float(carteira["usdbrl"]))
        except Exception as exc:
            logger.error("Falha no exterior: %s", exc)
    presentes_usd = [coluna for coluna in colunas_usd if coluna in df_usd.columns]
    usd_path = ROOT / "relatorios" / "exterior.csv"
    df_usd[presentes_usd].to_csv(usd_path, index=False)
    print("\n" + "=" * 110)
    print("         ALPHAAGENT - EXTERIOR USD (FASE 3.6)")
    print("         Mesma classificacao da acao. Preco_BRL usa usdbrl manual.")
    print("=" * 110)
    print(df_usd[presentes_usd].to_string(index=False))
    print("=" * 110)
    logger.info("Exterior gravado em %s", usd_path)

    colunas_fii = ["Ticker", "Preco_Atual", "PVP", "Dividend_Yield_%", "Status_FII"]
    df_fii = pd.DataFrame(columns=colunas_fii)
    try:
        lista_fii = carregar_watchlist(ROOT / "config" / "fiis.txt")
        bruto_fii = fetch_multiple_tickers(lista_fii)
        if not bruto_fii.empty:
            df_fii = classificar_fii(bruto_fii)
    except Exception as exc:
        logger.error("Falha nos FIIs: %s", exc)
    presentes_fii = [coluna for coluna in colunas_fii if coluna in df_fii.columns]
    fii_path = ROOT / "relatorios" / "fiis.csv"
    df_fii[presentes_fii].to_csv(fii_path, index=False)
    print("\n" + "=" * 90)
    print("         ALPHAAGENT - FUNDOS IMOBILIARIOS (FASE 3.8)")
    print("         P/VP abaixo de 1 e desconto. Nao e ordem.")
    print("=" * 90)
    print(df_fii[presentes_fii].to_string(index=False))
    print("=" * 90)
    logger.info("FIIs gravados em %s", fii_path)

    carteira_html = ROOT / "relatorios" / "carteira.html"
    gravar_carteira_html(alocacao, renda_fixa, df_usd[presentes_usd], df_fii[presentes_fii], carteira_html)
    logger.info("Carteira consolidada em %s", carteira_html)


if __name__ == "__main__":
    main()
