"""NALCO domestic aluminium price source.

nalcoindia.com publishes a "Metal Price" notification periodically (not on a fixed daily
schedule), so this is polled on its own interval (NALCO_FETCH_INTERVAL_HOURS, default 6h)
and the price_service layer only writes a new PricePoint row when the value actually
changes from the last stored one - see `record_nalco_price` in services/price_service.py.
"""

from datetime import datetime, timezone

import httpx
import re
from bs4 import BeautifulSoup

from app.adapters.base import PriceObservation, Source

UNIT = "INR/kg"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; CommodityDashboard/1.0; +https://example.local)"}
NALCO_URL = "https://nalcoindia.com/investor/metal-price/"


class NalcoScrapeSource(Source):
    name = "nalcoindia.com (scrape)"

    def is_configured(self) -> bool:
        return True

    async def fetch(self) -> list[PriceObservation]:
        async with httpx.AsyncClient(timeout=15, headers=HEADERS, follow_redirects=True) as client:
            resp = await client.get(NALCO_URL)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "lxml")
            text = soup.get_text(" ", strip=True)
            # NALCO notices read like "...Ingot price w.e.f. dd.mm.yyyy is Rs. XXX per Kg..."
            match = re.search(r"(?:Rs\.?|INR)\s*([\d,]+(?:\.\d+)?)\s*per\s*kg", text, re.IGNORECASE)
            if not match:
                raise ValueError("could not locate an 'Rs. X per Kg' price pattern on the NALCO metal-price page")
            price = float(match.group(1).replace(",", ""))
        return [
            PriceObservation(
                instrument="NALCO_ALUMINIUM", price=price, currency="INR", unit=UNIT,
                source="nalcoindia.com", source_url=NALCO_URL, as_of=datetime.now(timezone.utc),
            )
        ]


def build_nalco_sources() -> list[Source]:
    return [NalcoScrapeSource()]
