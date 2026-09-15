"""Background scheduler: each feed runs on its own interval and writes straight to the
DB, so the API layer only ever reads what's already stored - it never fetches on request."""

import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.adapters.base import Fetcher
from app.adapters.forex_adapter import build_forex_sources
from app.adapters.lme_adapter import build_lme_sources
from app.adapters.mcx_adapter import build_mcx_sources
from app.adapters.nalco_adapter import build_nalco_sources
from app.config import settings
from app.database import SessionLocal
from app.models import ForexRate
from app.services.price_service import mark_stale_snapshot, store_observations
from app.static_data import INSTRUMENTS

logger = logging.getLogger("scheduler")

lme_fetcher = Fetcher(build_lme_sources())
mcx_fetcher = Fetcher(build_mcx_sources())
nalco_fetcher = Fetcher(build_nalco_sources())
forex_fetcher = Fetcher(build_forex_sources())

LME_INSTRUMENTS = [k for k, v in INSTRUMENTS.items() if v["market"] == "LME"]
MCX_INSTRUMENTS = [k for k, v in INSTRUMENTS.items() if v["market"] == "MCX"]


async def run_lme_fetch():
    observations, error = await lme_fetcher.fetch_all()
    db = SessionLocal()
    try:
        if observations:
            n = store_observations(db, observations)
            logger.info("LME fetch stored %d observations", n)
        else:
            logger.warning("LME fetch failed on all sources (%s); marking stale snapshots", error)
            for instrument in LME_INSTRUMENTS:
                mark_stale_snapshot(db, instrument)
    finally:
        db.close()


async def run_mcx_fetch():
    observations, error = await mcx_fetcher.fetch_all()
    db = SessionLocal()
    try:
        if observations:
            n = store_observations(db, observations)
            logger.info("MCX fetch stored %d observations", n)
        else:
            logger.warning("MCX fetch failed on all sources (%s); marking stale snapshots", error)
            for instrument in MCX_INSTRUMENTS:
                mark_stale_snapshot(db, instrument)
    finally:
        db.close()


async def run_nalco_fetch():
    from app.services.price_service import record_nalco_price

    observations, error = await nalco_fetcher.fetch_all()
    db = SessionLocal()
    try:
        if observations:
            changed = record_nalco_price(db, observations[0])
            logger.info("NALCO fetch: %s", "new price recorded" if changed else "unchanged, no new row")
        else:
            logger.warning("NALCO fetch failed (%s); marking stale snapshot", error)
            mark_stale_snapshot(db, "NALCO_ALUMINIUM")
    finally:
        db.close()


async def run_forex_fetch():
    observations, error = await forex_fetcher.fetch_all()
    db = SessionLocal()
    try:
        if observations:
            for obs in observations:
                db.add(ForexRate(pair=obs.instrument, rate=obs.price, source=obs.source, as_of=obs.as_of))
            db.commit()
            logger.info("Forex fetch stored USDINR rate")
        else:
            logger.warning("Forex fetch failed on all sources (%s)", error)
    finally:
        db.close()


def start_scheduler() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(run_lme_fetch, "interval", minutes=settings.lme_fetch_interval_minutes, id="lme_fetch", next_run_time=None)
    scheduler.add_job(run_mcx_fetch, "interval", minutes=settings.mcx_fetch_interval_minutes, id="mcx_fetch", next_run_time=None)
    scheduler.add_job(run_nalco_fetch, "interval", hours=settings.nalco_fetch_interval_hours, id="nalco_fetch", next_run_time=None)
    scheduler.add_job(run_forex_fetch, "interval", minutes=settings.forex_fetch_interval_minutes, id="forex_fetch", next_run_time=None)
    scheduler.start()
    return scheduler
