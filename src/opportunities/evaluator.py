from typing import Optional

from .schemas import (
    OpportunityResultSchema,
    OpportunityRuleSchema,
    StatusRegraEnum,
)


class RuleEvaluator:
    def evaluate(
        self,
        rule: OpportunityRuleSchema,
        current_price: Optional[float],
        fair_value: Optional[float],
    ) -> OpportunityResultSchema:
        if self._incompleto(current_price, fair_value):
            return OpportunityResultSchema(
                ticker=rule.ticker,
                valuation_model=rule.valuation_model,
                status=StatusRegraEnum.INCOMPLETO,
                margem_atingida=None,
                preco_atual=current_price,
                valor_justo=fair_value,
            )

        margem = (fair_value - current_price) / fair_value

        if margem >= rule.limiar_compra:
            status = StatusRegraEnum.ZONA_COMPRA
        elif margem >= 0:
            status = StatusRegraEnum.OBSERVAR
        else:
            status = StatusRegraEnum.CARO

        return OpportunityResultSchema(
            ticker=rule.ticker,
            valuation_model=rule.valuation_model,
            status=status,
            margem_atingida=round(margem, 4),
            preco_atual=current_price,
            valor_justo=fair_value,
        )

    @staticmethod
    def _incompleto(current_price: Optional[float], fair_value: Optional[float]) -> bool:
        if current_price is None or fair_value is None:
            return True
        try:
            price = float(current_price)
            justo = float(fair_value)
        except (TypeError, ValueError):
            return True
        if price != price or justo != justo:
            return True
        return price <= 0 or justo <= 0
