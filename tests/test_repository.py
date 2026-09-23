import pandas as pd
from decimal import Decimal
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from src.db.database import Base
from src.db.models import Asset, AssetSnapshot
from src.db.repository import save_valuation_dataframe


def test_save_valuation_dataframe_persists_asset_and_snapshot():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    dataframe = pd.DataFrame(
        [{
            "Ticker": "PETR4",
            "Nome": "Petroleo Brasileiro",
            "Setor": "Energy",
            "Preco_Atual": 20.0,
            "PL": 10.0,
            "PVP": 2.0,
            "Dividend_Yield_%": 6.0,
            "Preco_Justo_Graham": 21.21,
            "Margem_Graham_%": 5.7,
            "Status_Coleta": "ok",
        }]
    )

    with Session(engine) as session:
        assert save_valuation_dataframe(session, dataframe) == 1
        asset = session.scalar(select(Asset).where(Asset.symbol == "PETR4"))
        snapshot = session.scalar(select(AssetSnapshot))

    assert asset is not None
    assert snapshot is not None
    assert snapshot.price == 20
    assert snapshot.graham_fair_price == Decimal("21.21")
