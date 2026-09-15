function fmtTime(iso) {
  if (!iso) return "—";
  const d = new Date(iso);
  return d.toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" });
}

function ChangeChip({ label, value }) {
  if (value === null || value === undefined) {
    return (
      <div style={{ textAlign: "center" }}>
        <div className="faint">{label}</div>
        <div className="dim">—</div>
      </div>
    );
  }
  const positive = value > 0;
  const color = value === 0 ? "var(--text-dim)" : positive ? "var(--bullish)" : "var(--bearish)";
  return (
    <div style={{ textAlign: "center" }}>
      <div className="faint">{label}</div>
      <div style={{ color, fontWeight: 600 }}>
        {positive ? "+" : ""}
        {value.toFixed(2)}%
      </div>
    </div>
  );
}

export default function PriceCard({ meta, latest, loading, error }) {
  if (loading) return <div className="panel">Loading price…</div>;
  if (error) return <div className="panel">Could not load price: {String(error.message || error)}</div>;
  if (!latest) return <div className="panel">No price data yet.</div>;

  return (
    <div className="panel" style={{ display: "flex", flexDirection: "column", gap: 12 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: 8 }}>
        <div>
          <div className="dim" style={{ fontSize: 13 }}>{meta.name}</div>
          <div style={{ fontSize: 32, fontWeight: 700, fontFamily: "var(--mono)" }}>
            {latest.currency === "USD" ? "$" : "₹"}
            {latest.price.toLocaleString(undefined, { maximumFractionDigits: 2 })}
            <span className="dim" style={{ fontSize: 14, fontWeight: 400, marginLeft: 6 }}>{latest.unit}</span>
          </div>
          {latest.inr_per_kg !== undefined && (
            <div className="dim mono" style={{ fontSize: 13 }}>
              ≈ ₹{latest.inr_per_kg.toLocaleString(undefined, { maximumFractionDigits: 2 })}/kg
              <span className="faint"> (@ USDINR {latest.fx_rate_used?.toFixed(2)})</span>
            </div>
          )}
        </div>
        <div style={{ textAlign: "right" }}>
          {latest.is_stale && <span className="tag tag-stale">STALE — last known value</span>}
        </div>
      </div>

      <div style={{ display: "flex", gap: 20 }}>
        <ChangeChip label="1D" value={latest.change_1d_pct} />
        <ChangeChip label="1W" value={latest.change_1w_pct} />
        <ChangeChip label="1M" value={latest.change_1m_pct} />
      </div>

      <div className="faint" style={{ borderTop: "1px solid var(--border)", paddingTop: 8 }}>
        Source: <strong>{latest.source || "unknown"}</strong> · As of {fmtTime(latest.as_of)} · Fetched {fmtTime(latest.fetched_at)}
        <br />
        Delayed / periodic data — not real-time. Never treat as an execution-grade quote.
      </div>
    </div>
  );
}
