"""USD/INR forex source, used only to convert LME USD/tonne quotes into INR/kg for
side-by-side comparison with MCX/NALCO - it does not replace those feeds.

1. RBIReferenceRateSource   - RBI's published reference rate (official, daily)
2. ExchangerateHostSource   - exchangerate.host, free, no key required
"""

from datetime import datetime, timezone

import httpx

from app.adapters.base import PriceObservation, Source
from app.config import settings

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; CommodityDashboard/1.0; +https://example.local)"}


class RBIReferenceRateSource(Source):
    name = "RBI reference rate"

    def is_configured(self) -> bool:
        return True

    async def fetch(self) -> list[PriceObservation]:
        # RBI publishes reference rates via its FBIL-hosted CSV/XML feed; the exact endpoint
        # changes periodically. Point RBI_REFERENCE_RATE_URL at the current one if you rely
        # on this being authoritative rather than the exchangerate.host fallback below.
        raise NotImplementedError("RBI reference rate feed URL not wired up - see comment above")


class ExchangerateHostSource(Source):
    name = "exchangerate.host"

    def is_configured(self) -> bool:
        return True

    async def fetch(self) -> list[PriceObservation]:
        params = {"base": "USD", "symbols": "INR"}
        if settings.forex_api_key:
            params["access_key"] = settings.forex_api_key
        async with httpx.AsyncClient(timeout=15, headers=HEADERS) as client:
            resp = await client.get("https://api.exchangerate.host/latest", params=params)
            resp.raise_for_status()
            data = resp.json()
            rate = float(data["rates"]["INR"])
        return [
            PriceObservation(
                instrument="USDINR", price=rate, currency="INR", unit="INR per USD",
                source="exchangerate.host", source_url="https://exchangerate.host",
                as_of=datetime.now(timezone.utc),
            )
        ]


def build_forex_sources() -> list[Source]:
    return [RBIReferenceRateSource(), ExchangerateHostSource()]
