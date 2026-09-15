from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import epc as epc_service
from app.services import price_service
from app.static_data import INSTRUMENTS

router = APIRouter(prefix="/api/epc", tags=["epc"])


@router.get("/bom-weights")
def list_bom_weights(db: Session = Depends(get_db)):
    rows = epc_service.get_bom_weights(db)
    return [
        {
            "instrument": r.instrument, "component": r.component,
            "weight_pct_of_module_cost": r.weight_pct_of_module_cost, "notes": r.notes,
        }
        for r in rows
    ]


class BomWeightUpdate(BaseModel):
    instrument: str
    component: str
    weight_pct_of_module_cost: float
    notes: str = ""


@router.put("/bom-weights")
def update_bom_weight(payload: BomWeightUpdate, db: Session = Depends(get_db)):
    if payload.instrument not in INSTRUMENTS:
        raise HTTPException(404, "unknown instrument")
    row = epc_service.upsert_bom_weight(db, payload.instrument, payload.component, payload.weight_pct_of_module_cost, payload.notes)
    return {"instrument": row.instrument, "component": row.component, "weight_pct_of_module_cost": row.weight_pct_of_module_cost, "notes": row.notes}


class LandedCostUpdate(BaseModel):
    freight_insurance_pct: float | None = None
    customs_duty_pct: float | None = None
    gst_pct: float | None = None
    trader_premium_inr_per_kg: float | None = None


@router.get("/landed-cost/{instrument}")
def get_landed_cost(instrument: str, db: Session = Depends(get_db)):
    if instrument not in INSTRUMENTS:
        raise HTTPException(404, "unknown instrument")
    cfg = epc_service.get_landed_cost_config(db, instrument)
    if not cfg:
        raise HTTPException(404, "no landed cost config for this instrument")

    latest = price_service.get_latest(db, instrument)
    if not latest:
        raise HTTPException(404, "no price data yet for this instrument")

    if price_service.is_lme(instrument):
        fx = price_service.get_latest_forex(db)
        if not fx:
            raise HTTPException(409, "no forex rate available to convert LME price to INR/kg")
        base_inr_per_kg = price_service.usd_tonne_to_inr_kg(latest.price, fx.rate)
    else:
        base_inr_per_kg = latest.price

    calc = epc_service.compute_landed_cost_inr_per_kg(base_inr_per_kg, cfg)
    calc["instrument"] = instrument
    calc["price_as_of"] = latest.as_of.isoformat()
    calc["price_source"] = latest.source
    calc["price_is_stale"] = latest.is_stale
    return calc


@router.put("/landed-cost/{instrument}")
def update_landed_cost(instrument: str, payload: LandedCostUpdate, db: Session = Depends(get_db)):
    if instrument not in INSTRUMENTS:
        raise HTTPException(404, "unknown instrument")
    cfg = epc_service.upsert_landed_cost_config(db, instrument, **payload.model_dump())
    return {
        "instrument": cfg.instrument, "freight_insurance_pct": cfg.freight_insurance_pct,
        "customs_duty_pct": cfg.customs_duty_pct, "gst_pct": cfg.gst_pct,
        "trader_premium_inr_per_kg": cfg.trader_premium_inr_per_kg,
    }


@router.get("/alerts")
def list_alerts(db: Session = Depends(get_db)):
    configs = epc_service.get_alert_configs(db)
    results = []
    now = datetime.now(timezone.utc)
    for cfg in configs:
        latest = price_service.get_latest(db, cfg.instrument)
        if not latest:
            continue
        reference = price_service.price_at_or_before(db, cfg.instrument, now - timedelta(days=cfg.window_days))
        change_pct = price_service.pct_change(latest.price, reference.price if reference else None)
        triggered = cfg.enabled and change_pct is not None and abs(change_pct) >= cfg.threshold_pct
        results.append({
            "instrument": cfg.instrument, "threshold_pct": cfg.threshold_pct, "window_days": cfg.window_days,
            "enabled": cfg.enabled, "change_pct": change_pct, "triggered": triggered,
            "current_price": latest.price, "unit": latest.unit,
        })
    return results


class AlertUpdate(BaseModel):
    threshold_pct: float
    window_days: int
    enabled: bool = True


@router.put("/alerts/{instrument}")
def update_alert(instrument: str, payload: AlertUpdate, db: Session = Depends(get_db)):
    if instrument not in INSTRUMENTS:
        raise HTTPException(404, "unknown instrument")
    cfg = epc_service.upsert_alert_config(db, instrument, payload.threshold_pct, payload.window_days, payload.enabled)
    return {"instrument": cfg.instrument, "threshold_pct": cfg.threshold_pct, "window_days": cfg.window_days, "enabled": cfg.enabled}
