"""LME price sources, tried in this order:

1. NasdaqDataLinkSource   - paid, exact, if NASDAQ_DATA_LINK_API_KEY is set
2. CustomFeedSource       - any broker/feed the user points CUSTOM_LME_FEED_URL at
3. TradingEconomicsScrape - free delayed HTML scrape of tradingeconomics.com/commodities
4. InvestingComScrape     - free delayed HTML scrape of investing.com commodity pages

Scrape sources are brittle by nature (site markup changes without notice) — that's why
they sit behind the paid/custom options and why the fetcher swallows their failures and
moves to the next source rather than raising.
"""

from datetime import datetime, timezone

import httpx
from bs4 import BeautifulSoup

from app.adapters.base import PriceObservation, Source
from app.config import settings
from app.static_data import LME_INSTRUMENTS

UNIT = "USD/tonne"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; CommodityDashboard/1.0; +https://example.local)"}

# metal -> Nasdaq Data Link dataset code (LME datasets under the LME/ database)
NASDAQ_DATASET_CODES = {
    "LME_ALUMINIUM": "LME/PR_AL",
    "LME_COPPER": "LME/PR_CU",
    "LME_ZINC": "LME/PR_ZN",
    "LME_LEAD": "LME/PR_PB",
    "LME_NICKEL": "LME/PR_NI",
    "LME_TIN": "LME/PR_SN",
}

# metal -> tradingeconomics.com commodity slug
TRADINGECONOMICS_SLUGS = {
    "LME_ALUMINIUM": "aluminum",
    "LME_COPPER": "copper",
    "LME_ZINC": "zinc",
    "LME_LEAD": "lead",
    "LME_NICKEL": "nickel",
    "LME_TIN": "tin",
}

# metal -> investing.com commodity path
INVESTING_SLUGS = {
    "LME_ALUMINIUM": "aluminum",
    "LME_COPPER": "copper",
    "LME_ZINC": "zinc",
    "LME_LEAD": "lead",
    "LME_NICKEL": "nickel",
    "LME_TIN": "tin",
}


class NasdaqDataLinkSource(Source):
    name = "Nasdaq Data Link (LME dataset)"

    def is_configured(self) -> bool:
        return bool(settings.nasdaq_data_link_api_key)

    async def fetch(self) -> list[PriceObservation]:
        observations = []
        async with httpx.AsyncClient(timeout=15) as client:
            for instrument, dataset in NASDAQ_DATASET_CODES.items():
                url = f"https://data.nasdaq.com/api/v3/datasets/{dataset}.json"
                resp = await client.get(url, params={"api_key": settings.nasdaq_data_link_api_key, "rows": 1})
                resp.raise_for_status()
                data = resp.json()["dataset"]
                latest_row = data["data"][0]
                as_of = datetime.strptime(latest_row[0], "%Y-%m-%d").replace(tzinfo=timezone.utc)
                price = float(latest_row[1])
                observations.append(
                    PriceObservation(
                        instrument=instrument, price=price, currency="USD", unit=UNIT,
                        source="Nasdaq Data Link", source_url=url, as_of=as_of,
                    )
                )
        return observations


class CustomFeedSource(Source):
    name = "Custom broker/LME feed"

    def is_configured(self) -> bool:
        return bool(settings.custom_lme_feed_url)

    async def fetch(self) -> list[PriceObservation]:
        headers = {"Authorization": f"Bearer {settings.custom_lme_feed_key}"} if settings.custom_lme_feed_key else {}
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(settings.custom_lme_feed_url, headers=headers)
            resp.raise_for_status()
            payload = resp.json()
        # Expected shape: [{"instrument": "LME_ALUMINIUM", "price": 2500.0, "as_of": "2025-01-01T00:00:00Z"}, ...]
        observations = []
        for row in payload:
            observations.append(
                PriceObservation(
                    instrument=row["instrument"], price=float(row["price"]), currency="USD", unit=UNIT,
                    source="custom feed", source_url=settings.custom_lme_feed_url,
                    as_of=datetime.fromisoformat(row["as_of"].replace("Z", "+00:00")),
                )
            )
        return observations


class TradingEconomicsScrapeSource(Source):
    name = "tradingeconomics.com (scrape)"

    def is_configured(self) -> bool:
        return True

    async def fetch(self) -> list[PriceObservation]:
        observations = []
        async with httpx.AsyncClient(timeout=15, headers=HEADERS, follow_redirects=True) as client:
            for instrument, slug in TRADINGECONOMICS_SLUGS.items():
                url = f"https://tradingeconomics.com/commodity/{slug}"
                resp = await client.get(url)
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, "lxml")
                price_el = soup.select_one("#p")
                if not price_el:
                    continue
                price = float(price_el.text.strip().replace(",", ""))
                observations.append(
                    PriceObservation(
                        instrument=instrument, price=price, currency="USD", unit=UNIT,
                        source="tradingeconomics.com", source_url=url, as_of=datetime.now(timezone.utc),
                    )
                )
        return observations


class InvestingComScrapeSource(Source):
    name = "investing.com (scrape)"

    def is_configured(self) -> bool:
        return True

    async def fetch(self) -> list[PriceObservation]:
        observations = []
        async with httpx.AsyncClient(timeout=15, headers=HEADERS, follow_redirects=True) as client:
            for instrument, slug in INVESTING_SLUGS.items():
                url = f"https://www.investing.com/commodities/{slug}"
                resp = await client.get(url)
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, "lxml")
                price_el = soup.select_one('[data-test="instrument-price-last"]')
                if not price_el:
                    continue
                price = float(price_el.text.strip().replace(",", ""))
                observations.append(
                    PriceObservation(
                        instrument=instrument, price=price, currency="USD", unit=UNIT,
                        source="investing.com", source_url=url, as_of=datetime.now(timezone.utc),
                    )
                )
        return observations


def build_lme_sources() -> list[Source]:
    return [NasdaqDataLinkSource(), CustomFeedSource(), TradingEconomicsScrapeSource(), InvestingComScrapeSource()]
