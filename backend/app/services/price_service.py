from datetime import datetime, timedelta, timezone
from statistics import mean

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.adapters.base import PriceObservation
from app.models import ForexRate, PricePoint
from app.static_data import INSTRUMENTS


def store_observations(db: Session, observations: list[PriceObservation]) -> int:
    count = 0
    for obs in observations:
        db.add(
            PricePoint(
                instrument=obs.instrument, price=obs.price, currency=obs.currency, unit=obs.unit,
                source=obs.source, source_url=obs.source_url, as_of=obs.as_of,
                fetched_at=datetime.now(timezone.utc), is_stale=False,
            )
        )
        count += 1
    db.commit()
    return count


def record_nalco_price(db: Session, observation: PriceObservation) -> bool:
    """Only write a new row when the NALCO price actually changed since the last entry."""
    last = (
        db.execute(
            select(PricePoint)
            .where(PricePoint.instrument == "NALCO_ALUMINIUM")
            .order_by(PricePoint.as_of.desc())
            .limit(1)
        )
        .scalars()
        .first()
    )
    if last and abs(last.price - observation.price) < 1e-9:
        return False
    store_observations(db, [observation])
    return True


def mark_stale_snapshot(db: Session, instrument: str) -> PricePoint | None:
    """When a fetch fails entirely, clone the last known price forward flagged as stale
    so the UI has something to show without ever presenting it as fresh."""
    last = get_latest(db, instrument)
    if not last:
        return None
    stale_point = PricePoint(
        instrument=instrument, price=last.price, currency=last.currency, unit=last.unit,
        source=last.source, source_url=last.source_url, as_of=last.as_of,
        fetched_at=datetime.now(timezone.utc), is_stale=True,
    )
    db.add(stale_point)
    db.commit()
    return stale_point


def get_latest(db: Session, instrument: str) -> PricePoint | None:
    return (
        db.execute(
            select(PricePoint).where(PricePoint.instrument == instrument).order_by(PricePoint.as_of.desc()).limit(1)
        )
        .scalars()
        .first()
    )


def get_latest_forex(db: Session, pair: str = "USDINR") -> ForexRate | None:
    return (
        db.execute(select(ForexRate).where(ForexRate.pair == pair).order_by(ForexRate.as_of.desc()).limit(1))
        .scalars()
        .first()
    )


def get_history(db: Session, instrument: str, since: datetime) -> list[PricePoint]:
    return (
        db.execute(
            select(PricePoint)
            .where(PricePoint.instrument == instrument, PricePoint.as_of >= since)
            .order_by(PricePoint.as_of.asc())
        )
        .scalars()
        .all()
    )


RANGE_TO_TIMEDELTA = {
    "1M": timedelta(days=30),
    "3M": timedelta(days=90),
    "6M": timedelta(days=182),
    "1Y": timedelta(days=365),
    "5Y": timedelta(days=365 * 5),
}


def price_at_or_before(db: Session, instrument: str, cutoff: datetime) -> PricePoint | None:
    return (
        db.execute(
            select(PricePoint)
            .where(PricePoint.instrument == instrument, PricePoint.as_of <= cutoff)
            .order_by(PricePoint.as_of.desc())
            .limit(1)
        )
        .scalars()
        .first()
    )


def pct_change(current: float, previous: float | None) -> float | None:
    if previous is None or previous == 0:
        return None
    return round((current - previous) / previous * 100, 2)


def compute_changes(db: Session, instrument: str, current_price: float, now: datetime) -> dict:
    day_ago = price_at_or_before(db, instrument, now - timedelta(days=1))
    week_ago = price_at_or_before(db, instrument, now - timedelta(days=7))
    month_ago = price_at_or_before(db, instrument, now - timedelta(days=30))
    return {
        "change_1d_pct": pct_change(current_price, day_ago.price if day_ago else None),
        "change_1w_pct": pct_change(current_price, week_ago.price if week_ago else None),
        "change_1m_pct": pct_change(current_price, month_ago.price if month_ago else None),
    }


def moving_averages(history: list[PricePoint]) -> dict:
    prices = [p.price for p in history]
    result = {}
    for window in (20, 50, 200):
        result[f"ma{window}"] = round(mean(prices[-window:]), 2) if len(prices) >= window else None
    return result


def trend_direction(history: list[PricePoint]) -> str:
    mas = moving_averages(history)
    if mas["ma20"] and mas["ma50"]:
        if mas["ma20"] > mas["ma50"]:
            return "uptrend"
        if mas["ma20"] < mas["ma50"]:
            return "downtrend"
    return "sideways"


def usd_tonne_to_inr_kg(usd_per_tonne: float, usdinr_rate: float) -> float:
    return round(usd_per_tonne * usdinr_rate / 1000, 2)


def is_lme(instrument: str) -> bool:
    return INSTRUMENTS[instrument]["market"] == "LME"
