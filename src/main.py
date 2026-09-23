import logging
from data.data_fetcher import fetch_multiple_tickers
from finance.engine import calculate_valuation

# Configuração de logs centralizada
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("AlphaAgent-Main")

def main() -> None:
    logger.info("Iniciando o AlphaAgent - Orquestrador (Fase 2 - Motor Financeiro)")

    # Watchlist Institucional inicial (4 ativos)
    watchlist_b3 = ["PETR4.SA", "VALE3.SA", "ITUB4.SA", "WEGE3.SA"]

    # 1. Extração de dados
    logger.info("Acionando o módulo de extração de dados...")
    try:
        df_raw = fetch_multiple_tickers(watchlist_b3)
    except Exception as e:
        logger.error(f"Falha na coleta de dados: {e}")
        return

    if df_raw.empty:
        logger.error("Nenhum dado retornado na extração.")
        return

    # 2. Execução do Motor Financeiro (Valuation)
    logger.info("Acionando o Motor Financeiro para cálculo de Valuation...")
    try:
        df_final = calculate_valuation(df_raw)
    except Exception as e:
        logger.error(f"Falha no cálculo do motor financeiro: {e}")
        return

    # 3. Exibição do Relatório Consolidado B2B com Valuation
    print("\n" + "=" * 125)
    print("                 ALPHAAGENT - RELATÓRIO INSTITUCIONAL DE VALUATION (FASE 2)")
    print("=" * 125)
    
    print(df_final.to_string(index=False))
    print("=" * 125)

if __name__ == "__main__":
    main()
    