"""Populates the DB with a demo price history on first run, so charts aren't empty
before the live scheduler has had time to accumulate real observations.

Every row this writes is tagged source="demo-seed (simulated)" and is_stale=True so the
UI never confuses it with a live fetch - the price cards will visibly say so. Real fetches
from the scheduler simply layer on top going forward with their own real source labels.
"""

import random
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import ForexRate, PricePoint
from app.static_data import INSTRUMENTS

SEED_SOURCE = "demo-seed (simulated)"

BASE_PRICES = {
    "LME_ALUMINIUM": 2450.0,
    "LME_COPPER": 9200.0,
    "LME_ZINC": 2750.0,
    "LME_LEAD": 2050.0,
    "LME_NICKEL": 16500.0,
    "LME_TIN": 31000.0,
    "MCX_COPPER": 830.0,
    "MCX_ALUMINIUM": 225.0,
    "NALCO_ALUMINIUM": 218.0,
}

DAILY_VOL_PCT = {
    "LME_ALUMINIUM": 0.9, "LME_COPPER": 1.1, "LME_ZINC": 1.2, "LME_LEAD": 1.0,
    "LME_NICKEL": 1.8, "LME_TIN": 1.6, "MCX_COPPER": 1.1, "MCX_ALUMINIUM": 0.9,
    "NALCO_ALUMINIUM": 0.3,
}

USDINR_BASE = 83.5


def db_is_empty(db: Session) -> bool:
    return db.execute(select(PricePoint).limit(1)).first() is None


def seed_demo_history(db: Session, days: int = 730) -> None:
    if not db_is_empty(db):
        return

    random.seed(42)
    now = datetime.now(timezone.utc)
    start = now - timedelta(days=days)

    # forex path first, since LME->INR display uses it
    fx_rate = USDINR_BASE
    fx_path = {}
    d = start
    while d <= now:
        fx_rate *= 1 + random.gauss(0, 0.002)
        fx_path[d.date()] = fx_rate
        db.add(ForexRate(pair="USDINR", rate=round(fx_rate, 4), source=SEED_SOURCE, as_of=d, is_stale=True))
        d += timedelta(days=1)

    for instrument, meta in INSTRUMENTS.items():
        price = BASE_PRICES[instrument]
        vol = DAILY_VOL_PCT[instrument] / 100
        d = start
        # gentle mean-reverting drift so the series looks plausible, not a pure random walk
        while d <= now:
            price *= 1 + random.gauss(0, vol)
            # mild pull back toward base to avoid runaway drift over 2 years
            price += (BASE_PRICES[instrument] - price) * 0.01
            db.add(
                PricePoint(
                    instrument=instrument, price=round(price, 2), currency=meta["currency"], unit=meta["unit"],
                    source=SEED_SOURCE, source_url="", as_of=d, fetched_at=now, is_stale=True,
                )
            )
            d += timedelta(days=1)

    db.commit()
