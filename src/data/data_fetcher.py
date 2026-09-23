import logging
import time
from typing import List, Dict, Any, Optional

import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)
RETRY_DELAYS_SECONDS = (0.5, 1.0)

def _to_percent(value: Any) -> Optional[float]:
    """Converte a fração decimal usada pelo yfinance para percentual."""
    if value is None:
        return None
    try:
        val = float(value)
        return round(val * 100, 2)
    except (TypeError, ValueError):
        return None

def fetch_multiple_tickers(tickers: List[str]) -> pd.DataFrame:
    """
    Coleta dados fundamentalistas em lote de tickers da B3
    e consolida em um DataFrame Pandas.

    Args:
        tickers: Lista de tickers no formato Yahoo (ex: ['PETR4.SA', 'VALE3.SA'])

    Returns:
        DataFrame com os dados consolidados
    """
    data_list: List[Dict[str, Any]] = []
    logger.info("Iniciando coleta para %d ativos: %s", len(tickers), tickers)

    for symbol in tickers:
        info = None
        last_error: Optional[Exception] = None
        for attempt in range(len(RETRY_DELAYS_SECONDS) + 1):
            try:
                info = yf.Ticker(symbol).info
                break
            except Exception as e:
                last_error = e
                if attempt < len(RETRY_DELAYS_SECONDS):
                    delay = RETRY_DELAYS_SECONDS[attempt]
                    logger.warning(
                        "Falha temporária ao consultar %s; nova tentativa em %.1fs",
                        symbol,
                        delay,
                    )
                    time.sleep(delay)

        if info is None:
            error_message = str(last_error or "resposta vazia da fonte")
            logger.error("Falha ao processar o ticker %s: %s", symbol, error_message)
            data_list.append({
                "Ticker": symbol.replace(".SA", ""),
                "Status_Coleta": "erro",
                "Erro_Coleta": error_message,
            })
            continue

        try:
            ticker_data = {
                "Ticker": symbol.replace(".SA", ""),
                "Nome": info.get("shortName") or info.get("longName") or "N/A",
                "Setor": info.get("sector", "N/A"),
                "Preco_Atual": info.get("currentPrice") or info.get("regularMarketPrice"),
                "PL": info.get("trailingPE"),
                "PVP": info.get("priceToBook"),
                "Dividend_Yield_%": _to_percent(info.get("dividendYield")),
                "ROE_%": _to_percent(info.get("returnOnEquity")),
                "Margem_Liquida_%": _to_percent(info.get("profitMargins")),
                "Market_Cap": info.get("marketCap"),
                "Fluxo_Caixa_Livre": info.get("freeCashflow"),
                "Acoes_Em_Circulacao": info.get("sharesOutstanding"),
                "Status_Coleta": "ok",
                "Erro_Coleta": None,
            }

            data_list.append(ticker_data)
            logger.info("Dados coletados com sucesso: %s", symbol)
        except (AttributeError, TypeError, ValueError) as e:
            logger.error("Dados inválidos para o ticker %s: %s", symbol, e)
            data_list.append({
                "Ticker": symbol.replace(".SA", ""),
                "Status_Coleta": "erro",
                "Erro_Coleta": str(e),
            })

    if not data_list:
        logger.warning("Nenhum dado foi coletado.")
        return pd.DataFrame()

    df = pd.DataFrame(data_list)
    return df


if __name__ == "__main__":
    # Teste Fase 1.5
    watchlist_b3 = ["PETR4.SA", "VALE3.SA", "ITUB4.SA", "WEGE3.SA"]

    df_consolidado = fetch_multiple_tickers(watchlist_b3)

    print("\n" + "=" * 60)
    print("      TABELA CONSOLIDADA ALPHAAGENT - B3 (Fase 1.5)")
    print("=" * 60)
    print(df_consolidado.to_string(index=False))
