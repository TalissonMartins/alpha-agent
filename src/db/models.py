from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(primary_key=True)
    symbol: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    name: Mapped[str | None] = mapped_column(String(255))
    sector: Mapped[str | None] = mapped_column(String(255))
    snapshots: Mapped[list["AssetSnapshot"]] = relationship(
        back_populates="asset", cascade="all, delete-orphan"
    )


class AssetSnapshot(Base):
    __tablename__ = "asset_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"), index=True)
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    status: Mapped[str] = mapped_column(String(20))
    error_message: Mapped[str | None] = mapped_column(Text)
    price: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    pe_ratio: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    pb_ratio: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    dividend_yield_percent: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    roe_percent: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    net_margin_percent: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    market_cap: Mapped[Decimal | None] = mapped_column(Numeric(24, 2))
    free_cash_flow: Mapped[Decimal | None] = mapped_column(Numeric(24, 2))
    shares_outstanding: Mapped[Decimal | None] = mapped_column(Numeric(24, 2))
    graham_fair_price: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    graham_margin_percent: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    gordon_fair_price: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    gordon_margin_percent: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    dcf_fair_price: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    dcf_margin_percent: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    earnings_yield_percent: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    asset: Mapped[Asset] = relationship(back_populates="snapshots")
