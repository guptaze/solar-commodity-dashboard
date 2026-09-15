from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import AlertConfig, BomWeight, LandedCostConfig
from app.static_data import DEFAULT_ALERTS, DEFAULT_BOM_WEIGHTS, DEFAULT_LANDED_COST


def ensure_defaults_seeded(db: Session) -> None:
    if not db.execute(select(BomWeight)).first():
        for row in DEFAULT_BOM_WEIGHTS:
            db.add(BomWeight(**row))
    if not db.execute(select(LandedCostConfig)).first():
        for instrument, cfg in DEFAULT_LANDED_COST.items():
            db.add(LandedCostConfig(instrument=instrument, **cfg))
    if not db.execute(select(AlertConfig)).first():
        for instrument, cfg in DEFAULT_ALERTS.items():
            db.add(AlertConfig(instrument=instrument, **cfg))
    db.commit()


def get_bom_weights(db: Session) -> list[BomWeight]:
    return db.execute(select(BomWeight)).scalars().all()


def upsert_bom_weight(db: Session, instrument: str, component: str, weight_pct: float, notes: str = "") -> BomWeight:
    existing = db.execute(
        select(BomWeight).where(BomWeight.instrument == instrument, BomWeight.component == component)
    ).scalar_one_or_none()
    if existing:
        existing.weight_pct_of_module_cost = weight_pct
        existing.notes = notes or existing.notes
        existing.updated_at = datetime.now(timezone.utc)
    else:
        existing = BomWeight(instrument=instrument, component=component, weight_pct_of_module_cost=weight_pct, notes=notes)
        db.add(existing)
    db.commit()
    db.refresh(existing)
    return existing


def get_landed_cost_config(db: Session, instrument: str) -> LandedCostConfig | None:
    return db.execute(select(LandedCostConfig).where(LandedCostConfig.instrument == instrument)).scalar_one_or_none()


def upsert_landed_cost_config(db: Session, instrument: str, **fields) -> LandedCostConfig:
    cfg = get_landed_cost_config(db, instrument)
    if not cfg:
        cfg = LandedCostConfig(instrument=instrument)
        db.add(cfg)
    for key, value in fields.items():
        if value is not None:
            setattr(cfg, key, value)
    cfg.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(cfg)
    return cfg


def compute_landed_cost_inr_per_kg(base_inr_per_kg: float, cfg: LandedCostConfig) -> dict:
    with_freight = base_inr_per_kg * (1 + cfg.freight_insurance_pct / 100)
    with_duty = with_freight * (1 + cfg.customs_duty_pct / 100)
    with_premium = with_duty + cfg.trader_premium_inr_per_kg
    with_gst = with_premium * (1 + cfg.gst_pct / 100)
    return {
        "base_inr_per_kg": round(base_inr_per_kg, 2),
        "after_freight_insurance": round(with_freight, 2),
        "after_customs_duty": round(with_duty, 2),
        "after_trader_premium": round(with_premium, 2),
        "landed_cost_inr_per_kg": round(with_gst, 2),
        "inputs": {
            "freight_insurance_pct": cfg.freight_insurance_pct,
            "customs_duty_pct": cfg.customs_duty_pct,
            "gst_pct": cfg.gst_pct,
            "trader_premium_inr_per_kg": cfg.trader_premium_inr_per_kg,
        },
    }


def get_alert_configs(db: Session) -> list[AlertConfig]:
    return db.execute(select(AlertConfig)).scalars().all()


def upsert_alert_config(db: Session, instrument: str, threshold_pct: float, window_days: int, enabled: bool) -> AlertConfig:
    cfg = db.execute(select(AlertConfig).where(AlertConfig.instrument == instrument)).scalar_one_or_none()
    if not cfg:
        cfg = AlertConfig(instrument=instrument)
        db.add(cfg)
    cfg.threshold_pct = threshold_pct
    cfg.window_days = window_days
    cfg.enabled = enabled
    cfg.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(cfg)
    return cfg
