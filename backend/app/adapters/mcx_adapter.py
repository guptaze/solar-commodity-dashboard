"""MCX near-month futures sources, tried in this order:

1. KiteConnectSource   - Zerodha Kite Connect, if KITE_* env vars are set
2. SmartAPISource      - Angel One SmartAPI, if SMARTAPI_* env vars are set
3. MCXScrapeSource     - free delayed scrape of mcxindia.com's public quotes page

MCX publishes prices in INR/kg for copper and INR/10kg for aluminium on its site; both
sources below normalise to INR/kg so downstream code never has to special-case the unit.
"""

from datetime import datetime, timezone

import httpx
from bs4 import BeautifulSoup

from app.adapters.base import PriceObservation, Source
from app.config import settings

UNIT = "INR/kg"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; CommodityDashboard/1.0; +https://example.local)"}

# MCX trading symbols for the near-month contract (rolled manually / via a cron that
# checks contract expiry - kept simple here since expiry dates are public and slow-moving)
MCX_SYMBOLS = {"MCX_COPPER": "COPPER", "MCX_ALUMINIUM": "ALUMINIUM"}
MCX_QUOTE_PATH = {"MCX_COPPER": "copper", "MCX_ALUMINIUM": "aluminium"}
# aluminium quotes are per 10kg on the exchange; normalise to per-kg
MCX_LOT_DIVISOR = {"MCX_COPPER": 1, "MCX_ALUMINIUM": 10}


class KiteConnectSource(Source):
    name = "Zerodha Kite Connect"

    def is_configured(self) -> bool:
        return bool(settings.kite_api_key and settings.kite_access_token)

    async def fetch(self) -> list[PriceObservation]:
        observations = []
        headers = {
            "X-Kite-Version": "3",
            "Authorization": f"token {settings.kite_api_key}:{settings.kite_access_token}",
        }
        async with httpx.AsyncClient(timeout=15, headers=headers) as client:
            for instrument, symbol in MCX_SYMBOLS.items():
                resp = await client.get(f"https://api.kite.trade/quote?i=MCX:{symbol}")
                resp.raise_for_status()
                payload = resp.json()["data"].get(f"MCX:{symbol}")
                if not payload:
                    continue
                price = float(payload["last_price"]) / MCX_LOT_DIVISOR[instrument]
                observations.append(
                    PriceObservation(
                        instrument=instrument, price=price, currency="INR", unit=UNIT,
                        source="Zerodha Kite Connect", source_url="https://kite.trade",
                        as_of=datetime.now(timezone.utc),
                    )
                )
        return observations


class SmartAPISource(Source):
    name = "Angel One SmartAPI"

    def is_configured(self) -> bool:
        return bool(settings.smartapi_api_key and settings.smartapi_client_id)

    async def fetch(self) -> list[PriceObservation]:
        # SmartAPI requires a login/session-token handshake (TOTP-based); left as a stub
        # since it needs interactive/short-lived tokens that can't be baked into env vars
        # safely. Wire this up with your own token-refresh flow if you have a SmartAPI account.
        raise NotImplementedError("SmartAPI session handshake not configured")


class MCXScrapeSource(Source):
    name = "mcxindia.com (scrape)"

    def is_configured(self) -> bool:
        return True

    async def fetch(self) -> list[PriceObservation]:
        observations = []
        async with httpx.AsyncClient(timeout=15, headers=HEADERS, follow_redirects=True) as client:
            for instrument, path in MCX_QUOTE_PATH.items():
                url = f"https://www.mcxindia.com/market-data/spot-market-price"
                resp = await client.get(url)
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, "lxml")
                row = soup.select_one(f'tr[data-commodity="{path}"] td.ltp')
                if not row:
                    continue
                price = float(row.text.strip().replace(",", "")) / MCX_LOT_DIVISOR[instrument]
                observations.append(
                    PriceObservation(
                        instrument=instrument, price=price, currency="INR", unit=UNIT,
                        source="mcxindia.com", source_url=url, as_of=datetime.now(timezone.utc),
                    )
                )
        return observations


def build_mcx_sources() -> list[Source]:
    return [KiteConnectSource(), SmartAPISource(), MCXScrapeSource()]
