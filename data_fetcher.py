import yfinance as yf

def obter_dados_ticker(ticker: str) -> dict:
    """
    Obtém indicadores fundamentais e cotação de ativos da B3.
    Adiciona o sufixo '.SA' automaticamente caso não esteja presente.
    """
    symbol = f"{ticker.upper()}.SA" if not ticker.endswith(".SA") else ticker.upper()
    ativo = yf.Ticker(symbol)
    info = ativo.info
    
    dados = {
        "symbol": ticker.upper(),
        "preco_atual": info.get("currentPrice") or info.get("regularMarketPrice"),
        "pvp": info.get("priceToBook"),
        "pl": info.get("trailingPE"),
        "dividend_yield": info.get("dividendYield"),
        "lucro_por_acao": info.get("trailingEps"),
        "valor_patrimonial_por_acao": info.get("bookValue"),
    }
    return dados

if __name__ == "__main__":
    ticker_teste = "BBAS3"
    print(f"--- A recolher dados para {ticker_teste} ---")
    dados = obter_dados_ticker(ticker_teste)
    for chave, valor in dados.items():
        print(f"{chave}: {valor}")

        