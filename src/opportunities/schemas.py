from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class StatusRegraEnum(str, Enum):
    ZONA_COMPRA = "ZONA_COMPRA"
    OBSERVAR = "OBSERVAR"
    CARO = "CARO"
    INCOMPLETO = "INCOMPLETO"


class ValuationModelEnum(str, Enum):
    GRAHAM = "GRAHAM"
    GORDON = "GORDON"
    EARNINGS_YIELD = "EARNINGS_YIELD"
    DCF = "DCF"


class OpportunityRuleSchema(BaseModel):
    ticker: str
    valuation_model: ValuationModelEnum
    limiar_compra: float = Field(default=0.20, ge=0.0, le=1.0)

    @field_validator("ticker")
    @classmethod
    def ticker_maiusculo(cls, value: str) -> str:
        return value.strip().upper()


class OpportunityResultSchema(BaseModel):
    ticker: str
    valuation_model: ValuationModelEnum
    status: StatusRegraEnum
    margem_atingida: Optional[float] = None
    preco_atual: Optional[float] = None
    valor_justo: Optional[float] = None
