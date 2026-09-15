from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ForexRate
from app.services import factors as factors_service
from app.services import price_service
from app.static_data import INSTRUMENTS

router = APIRouter(prefix="/api/commodities", tags=["commodities"])


def _serialize_point(p) -> dict:
    return {
        "price": p.price, "currency": p.currency, "unit": p.unit,
        "source": p.source, "source_url": p.source_url,
        "as_of": p.as_of.isoformat(), "fetched_at": p.fetched_at.isoformat(),
        "is_stale": p.is_stale,
    }


@router.get("")
def list_instruments():
    return [{"code": code, **meta} for code, meta in INSTRUMENTS.items()]


@router.get("/{instrument}/latest")
def get_latest(instrument: str, db: Session = Depends(get_db)):
    if instrument not in INSTRUMENTS:
        raise HTTPException(404, "unknown instrument")
    point = price_service.get_latest(db, instrument)
    if not point:
        raise HTTPException(404, "no price data yet for this instrument")

    result = {"instrument": instrument, **_serialize_point(point)}
    result.update(price_service.compute_changes(db, instrument, point.price, datetime.now(timezone.utc)))

    if price_service.is_lme(instrument):
        fx = price_service.get_latest_forex(db)
        if fx:
            result["inr_per_kg"] = price_service.usd_tonne_to_inr_kg(point.price, fx.rate)
            result["fx_rate_used"] = fx.rate
            result["fx_as_of"] = fx.as_of.isoformat()
    return result


@router.get("/{instrument}/history")
def get_history(instrument: str, range: str = Query("6M"), db: Session = Depends(get_db)):
    if instrument not in INSTRUMENTS:
        raise HTTPException(404, "unknown instrument")
    delta = price_service.RANGE_TO_TIMEDELTA.get(range)
    if not delta:
        raise HTTPException(400, f"range must be one of {list(price_service.RANGE_TO_TIMEDELTA)}")
    since = datetime.now(timezone.utc) - delta
    history = price_service.get_history(db, instrument, since)

    fx_by_date = {}
    if price_service.is_lme(instrument):
        for fx in db.execute(select(ForexRate)).scalars().all():
            fx_by_date[fx.as_of.date()] = fx.rate

    points = []
    for p in history:
        row = {"as_of": p.as_of.isoformat(), "price": p.price, "is_stale": p.is_stale, "source": p.source}
        if price_service.is_lme(instrument):
            rate = fx_by_date.get(p.as_of.date())
            if rate:
                row["inr_per_kg"] = price_service.usd_tonne_to_inr_kg(p.price, rate)
        points.append(row)
    return {"instrument": instrument, "range": range, "points": points}


@router.get("/{instrument}/expected-price")
def get_expected_price(instrument: str, db: Session = Depends(get_db)):
    if instrument not in INSTRUMENTS:
        raise HTTPException(404, "unknown instrument")
    since = datetime.now(timezone.utc) - price_service.RANGE_TO_TIMEDELTA["1Y"]
    history = price_service.get_history(db, instrument, since)
    if not history:
        raise HTTPException(404, "not enough history yet")
    mas = price_service.moving_averages(history)
    trend = price_service.trend_direction(history)
    lean = factors_service.directional_lean(instrument, trend)
    return {"instrument": instrument, **mas, "trend": trend, **lean}


@router.get("/{instrument}/factors")
def get_factors(instrument: str):
    if instrument not in INSTRUMENTS:
        raise HTTPException(404, "unknown instrument")
    return {"instrument": instrument, "factors": factors_service.get_factors_for_instrument(instrument)}
