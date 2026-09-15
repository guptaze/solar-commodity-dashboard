from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class PricePoint(Base):
    """One observed price for a market instrument, always carrying its source + timestamp."""

    __tablename__ = "price_points"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    instrument: Mapped[str] = mapped_column(String(32), index=True)  # e.g. "LME_ALUMINIUM", "MCX_COPPER", "NALCO_ALUMINIUM"
    price: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(8))
    unit: Mapped[str] = mapped_column(String(16))  # e.g. "USD/tonne", "INR/kg"
    source: Mapped[str] = mapped_column(String(64))  # e.g. "investing.com", "mcxindia.com", "nalcoindia.com"
    source_url: Mapped[str] = mapped_column(String(256), default="")
    as_of: Mapped[datetime] = mapped_column(DateTime(timezone=True))  # timestamp the source itself carries
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    is_stale: Mapped[bool] = mapped_column(Boolean, default=False)  # true when this row is a repeated last-known value


class ForexRate(Base):
    __tablename__ = "forex_rates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    pair: Mapped[str] = mapped_column(String(16), index=True)  # "USDINR"
    rate: Mapped[float] = mapped_column(Float)
    source: Mapped[str] = mapped_column(String(64))
    as_of: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    is_stale: Mapped[bool] = mapped_column(Boolean, default=False)


class BomWeight(Base):
    """User-editable BOM cost-stack weighting of a commodity in solar EPC scope."""

    __tablename__ = "bom_weights"
    __table_args__ = (UniqueConstraint("instrument", "component", name="uq_bom_instrument_component"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    instrument: Mapped[str] = mapped_column(String(32), index=True)
    component: Mapped[str] = mapped_column(String(64))  # e.g. "Module frames & mounting structures"
    weight_pct_of_module_cost: Mapped[float] = mapped_column(Float)
    notes: Mapped[str] = mapped_column(String(256), default="")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class LandedCostConfig(Base):
    """User-editable landed-cost calculator inputs per instrument."""

    __tablename__ = "landed_cost_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    instrument: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    freight_insurance_pct: Mapped[float] = mapped_column(Float, default=2.0)
    customs_duty_pct: Mapped[float] = mapped_column(Float, default=7.5)
    gst_pct: Mapped[float] = mapped_column(Float, default=18.0)
    trader_premium_inr_per_kg: Mapped[float] = mapped_column(Float, default=0.0)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class AlertConfig(Base):
    __tablename__ = "alert_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    instrument: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    threshold_pct: Mapped[float] = mapped_column(Float, default=5.0)
    window_days: Mapped[int] = mapped_column(Integer, default=30)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
