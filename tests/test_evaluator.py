import pytest

from src.opportunities.evaluator import RuleEvaluator
from src.opportunities.schemas import (
    OpportunityRuleSchema,
    StatusRegraEnum,
    ValuationModelEnum,
)


@pytest.fixture
def evaluator():
    return RuleEvaluator()


def test_zona_compra_acima_do_limiar(evaluator):
    rule = OpportunityRuleSchema(
        ticker="PETR4.SA",
        valuation_model=ValuationModelEnum.GRAHAM,
        limiar_compra=0.20,
    )
    resultado = evaluator.evaluate(rule, current_price=30.0, fair_value=40.0)
    assert resultado.status == StatusRegraEnum.ZONA_COMPRA
    assert resultado.margem_atingida == 0.25


def test_zona_compra_no_limiar_exato(evaluator):
    rule = OpportunityRuleSchema(
        ticker="PETR4.SA",
        valuation_model=ValuationModelEnum.GRAHAM,
        limiar_compra=0.20,
    )
    resultado = evaluator.evaluate(rule, current_price=32.0, fair_value=40.0)
    assert resultado.status == StatusRegraEnum.ZONA_COMPRA
    assert resultado.margem_atingida == 0.20


def test_observar_margem_positiva_abaixo_do_limiar(evaluator):
    rule = OpportunityRuleSchema(
        ticker="VALE3.SA",
        valuation_model=ValuationModelEnum.DCF,
        limiar_compra=0.20,
    )
    resultado = evaluator.evaluate(rule, current_price=35.0, fair_value=40.0)
    assert resultado.status == StatusRegraEnum.OBSERVAR
    assert resultado.margem_atingida == 0.125


def test_caro_quando_preco_acima_do_justo(evaluator):
    rule = OpportunityRuleSchema(
        ticker="WEGE3.SA",
        valuation_model=ValuationModelEnum.GRAHAM,
        limiar_compra=0.20,
    )
    resultado = evaluator.evaluate(rule, current_price=50.0, fair_value=12.0)
    assert resultado.status == StatusRegraEnum.CARO
    assert resultado.margem_atingida < 0


def test_incompleto_preco_zerado(evaluator):
    rule = OpportunityRuleSchema(
        ticker="ITUB4.SA",
        valuation_model=ValuationModelEnum.GORDON,
        limiar_compra=0.20,
    )
    resultado = evaluator.evaluate(rule, current_price=0.0, fair_value=40.0)
    assert resultado.status == StatusRegraEnum.INCOMPLETO
    assert resultado.margem_atingida is None


def test_incompleto_valor_justo_negativo(evaluator):
    rule = OpportunityRuleSchema(
        ticker="ITUB4.SA",
        valuation_model=ValuationModelEnum.GORDON,
        limiar_compra=0.20,
    )
    resultado = evaluator.evaluate(rule, current_price=20.0, fair_value=-1.0)
    assert resultado.status == StatusRegraEnum.INCOMPLETO


def test_incompleto_quando_justo_ausente(evaluator):
    rule = OpportunityRuleSchema(
        ticker="PETR4.SA",
        valuation_model=ValuationModelEnum.GORDON,
        limiar_compra=0.20,
    )
    resultado = evaluator.evaluate(rule, current_price=20.0, fair_value=None)
    assert resultado.status == StatusRegraEnum.INCOMPLETO
