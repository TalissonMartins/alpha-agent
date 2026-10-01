import logging
import time
from typing import Any, Dict, List, Optional

import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)
RETRY_DELAYS_SECONDS = (0.5, 1.0)


def _to_percent(value: Any, *, input_is_percent: bool = False) -> Optional[float]:
    if value is None:
        return None
    try:
        val = float(value)
    except (TypeError, ValueError):
        return None
    if input_is_percent or val > 1.5:
        return round(val, 2)
    return round(val * 100, 2)

def fetch_single_ticker(symbol: str) -> Dict[str, Any]:
    last_error: Optional[str] = None
    for delay in (0.0,) + RETRY_DELAYS_SECONDS:
        if delay:
            time.sleep(delay)
        try:
            info = yf.Ticker(symbol).info
            current_price = info.get("currentPrice") or info.get("regularMarketPrice")
            if not current_price:
                return {
                    "Ticker": symbol.replace(".SA", ""),
                    "Nome": info.get("shortName") or info.get("longName", "N/A"),
                    "Setor": info.get("sector", "N/A"),
                    "Preco_Atual": None,
                    "PL": info.get("trailingPE"),
                    "PVP": info.get("priceToBook"),
                    "Dividend_Yield_%": _to_percent(info.get("dividendYield")),
                    "ROE_%": _to_percent(info.get("returnOnEquity")),
                    "Market_Cap": info.get("marketCap"),
                    "Status_Coleta": "erro",
                    "Erro_Coleta": "Preco ausente",
                }
            return {
                "Ticker": symbol.replace(".SA", ""),
                "Nome": info.get("shortName") or info.get("longName", "N/A"),
                "Setor": info.get("sector", "N/A"),
                "Preco_Atual": float(current_price),
                "PL": info.get("trailingPE"),
                "PVP": info.get("priceToBook"),
                "Dividend_Yield_%": _to_percent(info.get("dividendYield")),
                "ROE_%": _to_percent(info.get("returnOnEquity")),
                "Market_Cap": info.get("marketCap"),
                "Status_Coleta": "ok",
                "Erro_Coleta": None,
            }
        except Exception as exc:
            last_error = str(exc)
            logger.warning("Falha temporaria em %s: %s", symbol, last_error)
    logger.error("Falha ao processar o ticker %s: %s", symbol, last_error)
    return {
        "Ticker": symbol.replace(".SA", ""),
        "Nome": "N/A",
        "Setor": "N/A",
        "Preco_Atual": None,
        "PL": None,
        "PVP": None,
        "Dividend_Yield_%": None,
        "ROE_%": None,
        "Market_Cap": None,
        "Status_Coleta": "erro",
        "Erro_Coleta": last_error,
    }


def fetch_multiple_tickers(tickers: List[str]) -> pd.DataFrame:
    logger.info("Iniciando coleta para %d ativos: %s", len(tickers), tickers)
    rows = [fetch_single_ticker(symbol) for symbol in tickers]
    df = pd.DataFrame(rows)
    if df.empty:
        logger.warning("Nenhum dado foi coletado.")
    return df
