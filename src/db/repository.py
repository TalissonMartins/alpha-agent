from datetime import datetime, timezone
from typing import Any

import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Asset, AssetSnapshot


def _value(row: pd.Series, column: str) -> Any:
    value = row.get(column)
    return None if pd.isna(value) else value


def save_valuation_dataframe(session: Session, dataframe: pd.DataFrame) -> int:
    """Persiste uma fotografia imutável dos dados e do valuation calculado."""
    collected_at = datetime.now(timezone.utc)
    saved = 0

    for _, row in dataframe.iterrows():
        symbol = str(_value(row, "Ticker"))
        if not symbol or symbol == "None":
            continue

        asset = session.scalar(select(Asset).where(Asset.symbol == symbol))
        if asset is None:
            asset = Asset(
                symbol=symbol,
                name=_value(row, "Nome"),
                sector=_value(row, "Setor"),
            )
            session.add(asset)
            session.flush()
        else:
            asset.name = _value(row, "Nome") or asset.name
            asset.sector = _value(row, "Setor") or asset.sector

        session.add(
            AssetSnapshot(
                asset_id=asset.id,
                collected_at=collected_at,
                status=_value(row, "Status_Coleta") or "ok",
                error_message=_value(row, "Erro_Coleta"),
                price=_value(row, "Preco_Atual"),
                pe_ratio=_value(row, "PL"),
                pb_ratio=_value(row, "PVP"),
                dividend_yield_percent=_value(row, "Dividend_Yield_%"),
                roe_percent=_value(row, "ROE_%"),
                net_margin_percent=_value(row, "Margem_Liquida_%"),
                market_cap=_value(row, "Market_Cap"),
                free_cash_flow=_value(row, "Fluxo_Caixa_Livre"),
                shares_outstanding=_value(row, "Acoes_Em_Circulacao"),
                graham_fair_price=_value(row, "Preco_Justo_Graham"),
                graham_margin_percent=_value(row, "Margem_Graham_%"),
                gordon_fair_price=_value(row, "Preco_Justo_Gordon"),
                gordon_margin_percent=_value(row, "Margem_Gordon_%"),
                dcf_fair_price=_value(row, "Preco_Justo_DCF"),
                dcf_margin_percent=_value(row, "Margem_DCF_%"),
                earnings_yield_percent=_value(row, "Earnings_Yield_%"),
            )
        )
        saved += 1

    session.commit()
    return saved
