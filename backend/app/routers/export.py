import csv
import io
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import price_service
from app.static_data import INSTRUMENTS

router = APIRouter(prefix="/api/export", tags=["export"])


def _snapshot_rows(db: Session) -> list[dict]:
    now = datetime.now(timezone.utc)
    fx = price_service.get_latest_forex(db)
    rows = []
    for instrument, meta in INSTRUMENTS.items():
        latest = price_service.get_latest(db, instrument)
        if not latest:
            continue
        row = {
            "instrument": instrument, "name": meta["name"], "market": meta["market"],
            "price": latest.price, "currency": latest.currency, "unit": latest.unit,
            "source": latest.source, "as_of": latest.as_of.isoformat(),
            "is_stale": latest.is_stale, "snapshot_taken_at": now.isoformat(),
        }
        if price_service.is_lme(instrument) and fx:
            row["inr_per_kg"] = price_service.usd_tonne_to_inr_kg(latest.price, fx.rate)
            row["fx_rate_used"] = fx.rate
        rows.append(row)
    return rows


@router.get("/bid-snapshot")
def export_bid_snapshot(format: str = Query("json", pattern="^(json|csv)$"), db: Session = Depends(get_db)):
    """Snapshot current commodity prices for a bid's costing sheet, so a BD person can
    timestamp the assumptions behind a techno-commercial offer."""
    rows = _snapshot_rows(db)
    if format == "json":
        return {"snapshot_taken_at": datetime.now(timezone.utc).isoformat(), "rows": rows}

    buf = io.StringIO()
    if rows:
        writer = csv.DictWriter(buf, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    buf.seek(0)
    filename = f"bid_costing_snapshot_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.csv"
    return StreamingResponse(
        iter([buf.getvalue()]), media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
