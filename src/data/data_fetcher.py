import logging
import time
from typing import Any, Dict, List, Optional

import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)
RETRY_DELAYS_SECONDS = (0.5, 1.0)


def _to_percent(value: Any, *, input_is_percent: bool = False) -> Optional[float]:
    """Decimal Yahoo (0.06) vira 6.0. Valor acima de 1.5 ja esta em percentual."""
    if value is None:
        return None
    try:
        val = float(value)
    except (TypeError, ValueError):
        return None
    if input_is_percent or val > 1.5:
        return round(val, 2)
    return round(val * 100, 2)


def dividend_yield_percent(info: Dict[str, Any], price: Optional[float]) -> Optional[float]:
    """Prefere dividendo anual / preco. Evita multiplicar yield que ja veio em percentual."""
    rate = info.get("dividendRate")
    if rate is None:
        rate = info.get("trailingAnnualDividendRate")
    if price and price > 0 and rate is not None:
        try:
            return round(float(rate) / float(price) * 100, 2)
        except (TypeError, ValueError):
            pass
    return _to_percent(info.get("dividendYield") or info.get("trailingAnnualDividendYield"))


def fetch_single_ticker(symbol: str) -> Dict[str, Any]:
    last_error: Optional[str] = None
    for delay in (0.0,) + RETRY_DELAYS_SECONDS:
        if delay:
            time.sleep(delay)
        try:
            info = yf.Ticker(symbol).info
            current_price = info.get("currentPrice") or info.get("regularMarketPrice")
            base = {
                "Ticker": symbol.replace(".SA", ""),
                "Nome": info.get("shortName") or info.get("longName", "N/A"),
                "Setor": info.get("sector", "N/A"),
                "PL": info.get("trailingPE"),
                "PVP": info.get("priceToBook"),
                "Dividend_Yield_%": dividend_yield_percent(info, float(current_price) if current_price else None),
                "ROE_%": _to_percent(info.get("returnOnEquity")),
                "Market_Cap": info.get("marketCap"),
            }
            if not current_price:
                return {
                    **base,
                    "Preco_Atual": None,
                    "Status_Coleta": "erro",
                    "Erro_Coleta": "Preco ausente",
                }
            return {
                **base,
                "Preco_Atual": float(current_price),
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
