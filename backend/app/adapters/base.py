"""Pluggable data-source adapter interface.

Every price feed (LME, MCX, NALCO, forex) is implemented as a chain of `Source` objects.
A `Fetcher` tries each source in order and returns the first successful result; if all
sources fail it returns None so the caller can fall back to the last stored value and
flag it stale. This is the seam to swap in a paid feed (Nasdaq Data Link, a broker API)
without touching scheduler or API code — just add a `Source` ahead of the scrapers in
the chain, gated on whether its env var is set.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


@dataclass
class PriceObservation:
    instrument: str
    price: float
    currency: str
    unit: str
    source: str
    source_url: str
    as_of: datetime


class Source(ABC):
    """One concrete way to get a price (a specific API or a specific scrape target)."""

    name: str = "unnamed-source"

    @abstractmethod
    def is_configured(self) -> bool:
        """Whether this source has what it needs (an API key, etc.) to even attempt a fetch."""

    @abstractmethod
    async def fetch(self) -> list[PriceObservation]:
        """Return whatever observations this source can produce. Raise on hard failure."""


class Fetcher:
    """Runs a prioritized list of Sources, returning the first that succeeds with data."""

    def __init__(self, sources: list[Source]):
        self.sources = sources

    async def fetch_all(self) -> tuple[list[PriceObservation], str | None]:
        for source in self.sources:
            if not source.is_configured():
                continue
            try:
                observations = await source.fetch()
                if observations:
                    return observations, None
            except Exception as exc:  # noqa: BLE001 - a broken scraper must not crash the scheduler
                last_error = f"{source.name}: {exc}"
                continue
        else:
            last_error = "no configured source produced data"
        return [], last_error
