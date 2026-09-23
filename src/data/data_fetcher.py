import logging
from typing import List, Dict, Any, Optional

import pandas as pd
import yfinance as yf

# Configuração de logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def _to_percent(value: Any) -> Optional[float]:
    """Converte valor para percentual com 2 casas. Trata escala inconsistente do yfinance."""
    if value is None:
        return None
    try:
        val = float(value)
        # Se o valor já parecer percentual (> 1.5), não multiplica por 100
        if val > 1.5:
            return round(val, 2)
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
    logging.info(f"Iniciando coleta para {len(tickers)} ativos: {tickers}")

    for symbol in tickers:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

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
            }

            data_list.append(ticker_data)
            logging.info(f"✔ Dados coletados com sucesso: {symbol}")

        except Exception as e:
            logging.error(f"❌ Falha ao processar o ticker {symbol}: {str(e)}")

    if not data_list:
        logging.warning("Nenhum dado foi coletado com sucesso.")
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
