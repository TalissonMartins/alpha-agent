import pandas as pd

from src.portfolio.mercado import escolher_ipca_mais, ipca_12m
from src.portfolio.mudancas import mudancas_de_status


def test_ipca_12m_composto():
    assert ipca_12m([1.0, 1.0]) == 2.01


def test_escolhe_ipca_mais_proximo_de_2029():
    texto = (
        "Tipo Titulo;Data Vencimento;Data Base;Taxa Compra Manha;Taxa Venda Manha\n"
        "Tesouro IPCA+;15/08/2024;31/12/2015;7,35;7,20\n"
        "Tesouro IPCA+;15/08/2029;02/10/2026;6,91;6,80\n"
        "Tesouro IPCA+;15/05/2050;02/10/2026;6,32;6,20\n"
        "Tesouro IPCA+ com Juros Semestrais;15/08/2032;02/10/2026;6,50;6,40\n"
    )
    detalhe = escolher_ipca_mais(texto, 2029)
    assert detalhe["taxa"] == 6.91
    assert detalhe["vencimento"] == "15/08/2029"
    assert detalhe["data_base"] == "02/10/2026"


def test_sem_dois_dias_nao_ha_mudanca():
    historico = pd.DataFrame(
        [{"data": "2026-10-05", "classe": "RV_BR", "ativo": "PETR4", "modelo": "GRAHAM", "status": "CARO"}]
    )
    assert mudancas_de_status(historico).empty


def test_detecta_troca_de_status():
    historico = pd.DataFrame(
        [
            {"data": "2026-10-04", "classe": "RV_BR", "ativo": "PETR4", "modelo": "GRAHAM", "status": "OBSERVAR"},
            {"data": "2026-10-05", "classe": "RV_BR", "ativo": "PETR4", "modelo": "GRAHAM", "status": "ZONA_COMPRA"},
        ]
    )
    mudou = mudancas_de_status(historico)
    assert len(mudou) == 1
    assert mudou.loc[0, "status_atual"] == "ZONA_COMPRA"
