# Solar EPC Commodity Intelligence Dashboard

Tracks non-ferrous metal prices (LME, MCX, NALCO) relevant to solar EPC/BESS cost
structures, surfaces the macro factors driving them, and layers on EPC-specific tools
(BOM exposure, landed-cost calculator, threshold alerts, bid-snapshot export).

**All pricing is delayed/periodic, never real-time.** Every price carries a source and
an "as of" timestamp in the UI, and a stale flag when a fetch fails and the last known
value is shown instead.

## Architecture

```
backend/   FastAPI + SQLite (SQLAlchemy) + APScheduler
  app/adapters/    pluggable Source/Fetcher interface per feed (LME, MCX, NALCO, forex)
  app/services/    price math (MAs, % change), factor scoring, EPC calculators
  app/routers/     REST API
  app/scheduler.py background jobs, one per feed, own interval, writes straight to DB
  app/seed.py      demo history seeded on first run (clearly source-tagged as simulated)
frontend/  React (Vite) + Recharts
```

The API never fetches on request — it only reads what the scheduler already wrote to
the DB, per the requirement that this stay delayed/periodic rather than live.

### Data sources & fallback chains

- **LME**: Nasdaq Data Link (if `NASDAQ_DATA_LINK_API_KEY` set) → your own broker/feed
  (`CUSTOM_LME_FEED_URL`) → tradingeconomics.com scrape → investing.com scrape.
- **MCX**: Zerodha Kite Connect (if `KITE_*` set) → Angel One SmartAPI (stubbed — needs
  your own TOTP session handshake) → mcxindia.com public quotes scrape.
- **NALCO**: nalcoindia.com "Metal Price" notice scrape, polled every
  `NALCO_FETCH_INTERVAL_HOURS` (default 6h); a new DB row is only written when the price
  actually changes from the last stored value.
- **Forex** (LME USD/tonne → INR/kg): RBI reference rate (stub — wire up the current
  FBIL feed URL) → exchangerate.host (free, no key).

Each feed is a `Fetcher` trying a prioritized list of `Source` objects
(`app/adapters/base.py`) — add a new one ahead of the scrapers to plug in a paid feed
without touching the scheduler or API. Scrapers are inherently brittle (site markup
changes without notice); a broken one is swallowed and the fetcher moves to the next
source, or the API falls back to the last stored price flagged `is_stale: true`.

### Demo data

On first run with an empty DB, `app/seed.py` generates ~2 years of synthetic history per
instrument so the charts aren't empty before the scheduler has accumulated real data.
Every seeded row is tagged `source: "demo-seed (simulated)"` and `is_stale: true` so it's
never confused with a live fetch in the UI.

## Running it

### Backend

```bash
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in any API keys you have; all are optional
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env   # points at the backend; defaults to http://localhost:8000
npm run dev
```

Open http://localhost:5173.

## EPC-specific layer

- **BOM exposure mapping** (`EPC Tools` tab): editable weighting of aluminium/copper/zinc
  in total module/BOS cost — starting estimates, not authoritative for any specific
  project's BOM.
- **Landed-cost calculator** (per LME commodity view): LME/MCX price → freight &
  insurance → customs duty → trader premium → GST → landed INR/kg, all inputs editable
  since duty/premium move with policy and vendor.
- **Threshold alerts** (`EPC Tools` tab): per-instrument % move over N days; a banner at
  the top of the app surfaces any triggered alert regardless of which tab you're on.
- **Bid costing export**: snapshots every instrument's latest price + timestamp + source
  to CSV or JSON, for a BD person to timestamp the assumptions behind a techno-commercial
  offer.

## Notes / known limitations

- The site scrapers (tradingeconomics, investing.com, mcxindia, nalcoindia) encode
  today's markup as CSS selectors / regex. These sites change layout periodically —
  expect to need to update a selector within weeks, which is exactly why the adapter
  interface exists.
- SmartAPI and the RBI reference-rate source are left as stubs (`NotImplementedError`)
  since both need an interactive/short-lived credential flow that can't be safely baked
  into a static env var — wire up your own token refresh if you rely on them.
- MCX contract symbols are the near-month contract as configured today; MCX rolls
  contracts monthly, so `MCX_SYMBOLS`/expiry handling in `mcx_adapter.py` will need a
  small scheduled roll job for unattended long-term use.
