from src.data.data_fetcher import dividend_yield_percent


def test_aapl_usa_dividendo_anual_sobre_preco():
    info = {"dividendYield": 0.44, "dividendRate": 1.04}
    assert dividend_yield_percent(info, 333.69) == 0.31


def test_b3_decimal_continua_em_percentual_quando_nao_ha_rate():
    info = {"dividendYield": 0.0883}
    assert dividend_yield_percent(info, None) == 8.83


def test_b3_que_ja_vem_em_percentual_nao_multiplica():
    info = {"dividendYield": 8.83}
    assert dividend_yield_percent(info, None) == 8.83
